"""Conservative explicit-grammar baseline. Unknown wording abstains, never invents data."""
import copy,datetime as dt,re
from scripts.benchmark import REQUIRED

NUM={'one':1,'two':2,'three':3,'five':5,'fifteen':15,'thirty':30,'forty-five':45,'sixty':60,'ninety':90,'an':1,'a':1}

def interpret(text,context,catalog,*,schema_version=1):
    if type(schema_version) is not int or schema_version not in (1,2):raise ValueError("Unknown intent version")
    if not isinstance(text,str) or len(text)>2000:raise ValueError('Request must be at most 2000 characters')
    x={'schema_version':schema_version,'status':'ready',**{f:context.get(f) for f in REQUIRED},'excluded_lift_types':[],
       'preferred_difficulties':[],'prefer_variety':False,'clarification_fields':[],'unsupported_preferences':[]}
    if schema_version==2:x['avoided_lift_types']=[]
    working=text.lower().strip();recognized=[]
    def consume(pattern,action):
        nonlocal working
        def sub(m):
            action(m);recognized.append(m.group(0));return ' '
        working=re.sub(pattern,sub,working,flags=re.I)
    def setfield(k,v):x[k]=v
    def exclude(values):x['excluded_lift_types']=sorted(set(x['excluded_lift_types'])|set(values))
    # Unsupported domain capabilities are explicit, including extra unfamiliar wording.
    for pattern,code in [(r'\b(?:shortest|live|current) queues(?: right now)?\b','live_queue_times'),(r'\bfreshly groomed(?: pistes)?(?: today)?\b','live_grooming'),(r'\boff[- ]piste(?: descent)?\b','off_piste'),(r'\b(?:quiet|uncrowded)(?: pistes)?\b','crowding')]:
        consume(pattern,lambda m,c=code:x['unsupported_preferences'].append(c))
    consume(r"\b(?:do not|don't) need (?:you )?to avoid (?:gondolas|drag lifts)\b",lambda m:None)
    def lift_rule(m,values):
        if schema_version==2 and m.group(0).lower().startswith('avoid'):
            x['avoided_lift_types']=sorted(set(x['avoided_lift_types'])|set(values))
        else:exclude(values)
    consume(r'\b(?:no|avoid(?: all)?|without) surface lifts(?:,? including carpets)?\b',lambda m:lift_rule(m,['platter','rope-tow','t-bar','magic-carpet']))
    consume(r'\b(?:no|avoid|without|skip all) drag lifts\b',lambda m:lift_rule(m,['platter','rope-tow','t-bar']))
    for phrase,typ in [('t-bars','t-bar'),('gondolas','gondola'),('cable cars','cable-car'),('chairlifts','chairlift'),('chairs','chairlift'),('rope tows','rope-tow'),('carpets','magic-carpet')]:
        consume(r'\b(?:no|skip|avoid|without) '+phrase+r'\b',lambda m,t=typ:lift_rule(m,[t]))
    if schema_version==2:x['avoided_lift_types']=sorted(set(x['avoided_lift_types'])-set(x['excluded_lift_types']))
    hard=[]
    grades='green|blue|red|black' if schema_version==2 else 'blue|red|black'
    if schema_version==2:
        def target_grade(m):
            hard.append(m.group(1));x['preferred_difficulties'].append(m.group(1))
        consume(r'\b(?:stay on|keep it) ('+grades+r')(?: descents| runs| pistes)?\b',target_grade)
    consume(r'\b(?:only|just) ('+grades+r')(?: pistes| runs|s)?\b',lambda m:hard.append(m.group(1)))
    consume(r'\b('+grades+r')(?: pistes| runs|s)? only\b',lambda m:hard.append(m.group(1)))
    if hard:
        x['hard_max_difficulty']=hard[-1]
        if len(set(hard))>1:x['hard_max_difficulty']=None;x['clarification_fields'].append('hard_max_difficulty')
    consume(r'\b(?:mostly|prefer|would prefer) ('+grades+r')(?: pistes| runs|s)?\b',lambda m:x['preferred_difficulties'].append(m.group(1)))
    consume(r'\b('+grades+r')s? (?:are|is) (?:okay|ok|fine)(?: too)?\b',lambda m:setfield('hard_max_difficulty',m.group(1)) if not hard else None)
    consume(r'\b(?:different|varied) pistes(?: rather than repeat them)?\b',lambda m:setfield('prefer_variety',True))
    consume(r'\b(?:variety|avoid repeats)\b',lambda m:setfield('prefer_variety',True))
    consume(r'\b(?:an?|one) hour and a half\b',lambda m:setfield('duration_minutes',90))
    def duration(m):
        n=int(m.group(1)) if m.group(1).isdigit() else NUM[m.group(1)]
        x['duration_minutes']=n*(60 if m.group(2).startswith('hour') else 1)
    consume(r'\b(\d+|one|two|three|five|fifteen|thirty|forty-five|sixty|ninety|an|a)[ -]+(minutes?|hours?)\b',duration)
    def deadline(m):
        if not x['start_time']:x['clarification_fields'].append('start_time');return
        start=dt.datetime.fromisoformat(x['start_time']);v=m.group(1)
        h,minute=(12,0) if v=='noon' else map(int,v.split(':'))
        if h>23 or minute>59:x['duration_minutes']=None;return
        cap=int((start.replace(hour=h,minute=minute,second=0)-start).total_seconds()/60)
        x['duration_minutes']=min(cap,x['duration_minutes']) if x['duration_minutes'] is not None else cap
    consume(r'\b(?:back|return|back at (?:the )?base|back at pine base)?\s*by (noon|\d{1,2}:\d{2})\b',deadline)
    # Place syntax is deliberately explicit; matching never introduces a new ID.
    aliases={a.casefold():p['id'] for p in catalog for a in [p['label']]+p.get('aliases',[])}
    def place(m):
        field='start_place_id' if m.group(1)=='start' else 'finish_place_id';label=m.group(2).strip()
        label=re.sub(r' instead of .*','',label)
        if label in aliases:x[field]=aliases[label]
        else:x[field]=None;x['clarification_fields'].append(field)
    consume(r'\b(start|finish) at ([\w -]+?)(?=\s+and\s+|[.,;]|$)',place)
    if x['duration_minutes'] is not None and (not 15<=x['duration_minutes']<=240 if schema_version==1 else x['duration_minutes']<=0):x['duration_minutes']=None
    for field in REQUIRED:
        if x[field] is None:x['clarification_fields'].append(field)
    # Only generic politeness/framing can be ignored. Other residuals force abstention.
    residue=re.sub(r'\b(?:please|i|have|can|ski|give|me|an|a|the|and|but|for|outing|plan|using|my|selected|settings|want|to|try|include|it|of|get|be|must|choose|lifts|with|route|find)\b',' ',working)
    residue=re.sub(r'[^\w:]+',' ',residue).strip()
    if residue:x['unsupported_preferences'].append('unparsed_request')
    for k in ['excluded_lift_types','preferred_difficulties','clarification_fields','unsupported_preferences']:x[k]=sorted(set(x[k]))
    x['status']='unsupported' if x['unsupported_preferences'] else 'clarify' if x['clarification_fields'] else 'ready'
    return {'intent':x,'adapter':'rules-v'+str(schema_version),'recognized':recognized,'unparsed':residue}
