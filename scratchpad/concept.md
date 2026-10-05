# Provisional direction: Pocket Field Missions

**Hypothesis, not a selected or implemented product.** A small model turns a person's time, mobility preferences and a supplied description of nearby outdoor space into one short, feasible observation mission. Read it, pocket the phone, spend 10–20 minutes outside, then optionally record what you noticed.

Example: a seated visitor with 12 minutes in a public garden receives a quiet sound-and-shadow observation task rather than an unsuitable walking route.

The narrow training task would be constraint-aware mission generation: obey time, terrain and mobility limits; ground references in supplied facts; produce a concise, structured card. Do not infer accessibility from missing data, invent trail facts, encourage wildlife disturbance, or provide foraging advice. No precise location is needed for an initial demo.

Why this might fit Tinker: domain-specific examples can teach compact, constraint-faithful outputs, with baseline-versus-tuned comparisons of all-constraints-pass rate, factual grounding and usefulness. Evaluate naturalness/usefulness through a blinded rubric alongside machine checks; token count alone is not quality.

**Kill criterion:** if a competent prompt or a small template/rules system already solves the task well, choose a better task rather than manufacturing a fine-tuning win. Validate this direction against alternatives before committing to an application build.
