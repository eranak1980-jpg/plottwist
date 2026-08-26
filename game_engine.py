import random

def build_case(players, location, inside_joke='', mode='murder'):
    names=[p['name'] for p in players]
    culprit=random.choice(names)
    victim='Alex Rosen' if mode=='murder' else ('the Midnight Diamond' if mode=='heist' else 'the leaked file')
    place=location or 'the living room'
    joke=' '.join((inside_joke or '').split())
    innocent=[n for n in names if n!=culprit]
    decoy=innocent[0] if innocent else names[0]
    witness=innocent[-1] if innocent else names[0]
    title=f'The Eight Seconds at {place}'
    opening=(f'11:47 PM. The lights go out at {place}. Eight seconds later they return. '
             f'{victim} is gone' if mode!='murder' else
             f'11:47 PM. The lights go out at {place}. Eight seconds later they return. {victim} is found beside the table.')
    opening += ' The back door is open. A glass is broken. Nobody has entered or left.'
    evidence=[
      {'id':'door','round':2,'title':'The Back Door','text':f'A photo timestamped 11:43 PM shows the back door was already open four minutes before the blackout. This weakens the obvious theory against {decoy}.'},
      {'id':'timeline','round':3,'title':'The Eight-Second Gap','text':f'A device log proves someone moved through {place} during the eight-second blackout. One earlier timeline can no longer be true.'},
    ]
    if joke:
      evidence.insert(1,{'id':'personal','round':2,'title':'The Personal Reference','text':f'A draft message on {victim}’s phone refers to a memory only this group should recognize: “{joke}”. It was left deliberately, not by accident.'})
    roles={}
    for i,n in enumerate(names):
      if n==culprit:
        roles[n]={'role':'The Culprit','secret':f'You caused what happened during the eight-second blackout. The open door is a decoy you want the group to focus on.','objective':f'Keep your timeline consistent and redirect suspicion toward {decoy}.','knows':['The back door is a staged distraction.']}
      elif n==witness:
        roles[n]={'role':'The Witness','secret':f'Before the blackout you saw {culprit} close to {place}, but admitting exactly where you were will expose a harmless lie of your own.','objective':'Reveal enough to help solve the case without exposing your whole secret too early.','knows':[f'{culprit} was closer to the scene than they may admit.']}
      else:
        roles[n]={'role':'The Secret Keeper','secret':f'{victim} privately warned you that someone in the group was preparing a distraction.','objective':'Work out which clue is genuine and which was planted.','knows':['The most obvious clue may be staged.']}
    rounds=[
      {'number':1,'name':'THE ALIBIS','public':opening+' Each player gives a one-sentence alibi. Keep private information hidden.'},
      {'number':2,'name':'THE EVIDENCE','public':'New evidence changes the obvious theory. Read the evidence cards and challenge one player whose story no longer fits.'},
      {'number':3,'name':'THE CONTRADICTION','public':'A new timestamp creates a contradiction. Each player must defend one exact part of their timeline.'},
      {'number':4,'name':'THE ACCUSATION','public':'Build your final theory: who did it, what was staged, and which clue proves it? Then vote in secret.'},
    ]
    reveal={'headline':f'{culprit} was the culprit.','timeline':[f'11:43 — the back door was already open.',f'11:47 — the lights went out for eight seconds.',f'During the blackout, {culprit} acted and relied on the open door as a false lead.',f'The contradiction in the timeline exposed the setup.'],'missed_clue':'The open door looked important because it was meant to look important.'}
    return {'title':title,'victim':victim,'culprit':culprit,'opening':opening,'roles':roles,'evidence':evidence,'rounds':rounds,'reveal':reveal}

def public_round(case, number):
    r=case['rounds'][number-1]
    ev=[e for e in case['evidence'] if e['round']==number]
    return {'number':number,'name':r['name'],'public':r['public'],'evidence':ev}
