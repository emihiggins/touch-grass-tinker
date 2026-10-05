"""Original tiny synthetic graphs. Not representations of real ski terrain."""
from .core import digest

def graph():
    edges=[]
    for eid,a,b,kind,difficulty,lift,duration,length in [
        ('chair','base','summit','lift',None,'chairlift',300,800),
        ('blue','summit','base','piste','blue',None,300,1200),
        ('red','summit','base','piste','red',None,200,900),
        ('tow','base','mid','lift',None,'rope-tow',90,100),
        ('practice','mid','base','piste','blue',None,90,150)]:
        edges.append({'id':eid,'from':a,'to':b,'kind':kind,'difficulty':difficulty,'lift_type':lift,'duration_s':duration,'length_m':length,'review_status':'synthetic','duration_basis':'assumed'})
    return {'schema_version':1,'id':'synthetic-pine-v1','timezone':'Europe/Vienna','difficulty_convention':'AT','review_status':'synthetic','nodes':[{'id':n} for n in ['base','summit','mid']],'edges':edges}

def scenario(g):
    return {'id':'simulated-winter-v1','simulated':True,'date':'2027-01-15','graph_hash':digest(g),
      'edges':{e['id']:{'status':'open','queue_s':0,'opens_at':'2027-01-15T09:00:00+01:00','closes_at':'2027-01-15T16:00:00+01:00'} for e in g['edges']}}

def intent():
    return {'status':'ready','start_place_id':'base','finish_place_id':'base','start_time':'2027-01-15T10:00:00+01:00','duration_minutes':30,'hard_max_difficulty':'blue','excluded_lift_types':[],'preferred_difficulties':['blue'],'prefer_variety':True}
