from game_engine import build_case,public_round

def test_case():
 p=[{'id':1,'name':'Eran'},{'id':2,'name':'Daniel'},{'id':3,'name':'Akiva'}]
 c=build_case(p,'living room','Daniel once burned the pasta water','murder')
 assert c['culprit'] in {'Eran','Daniel','Akiva'}
 assert len(c['roles'])==3
 assert len(c['rounds'])==4
 assert any('pasta' in e['text'] for e in c['evidence'])
 assert public_round(c,1)['name']=='THE ALIBIS'
 assert public_round(c,2)['name']=='THE EVIDENCE'
 assert public_round(c,3)['name']=='THE CONTRADICTION'
 assert public_round(c,4)['name']=='THE ACCUSATION'
 assert len(c['reveal']['timeline'])>=4

if __name__=='__main__':
 test_case();print('PlotTwist 2 engine smoke test passed')
