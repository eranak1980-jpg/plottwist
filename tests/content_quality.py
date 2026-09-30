"""Focused, offline checks for the curated and AI-generated question safety net."""
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from kyc_ai import clean_pack
from kyc_locales import SUPPORTED_LANGUAGES,last_resort,ui_copy
from kyc_questions import GENERAL


def key(value):
    return re.sub(r'\W+','',value,flags=re.UNICODE).casefold()


duo=[question for question in GENERAL if question[0]=='know' and len(question[2])==4]
assert len(duo)>=18,len(duo)
assert len({key(text) for _,text,_ in duo})==len(duo)
assert sum(12<=len(text.split())<=24 for _,text,_ in duo)>=18
for _,text,options in duo:
    assert '{s}' in text,text
    assert all('{s}' not in option for option in options),(text,options)
    assert len({key(option) for option in options})==4,(text,options)
print('CONTENT_HEBREW_DUO_FALLBACK_OK')


good=[
 {'type':'know','text':'{s} finds a mystery invitation under the door tonight. What happens next?','options':['Calls the venue','Brings one friend','Goes there alone','Asks the group chat']},
 {'type':'know','text':'{s} is locked outside ten minutes before guests arrive. What is the first move?','options':['Calls a locksmith','Climbs through a window','Moves dinner next door','Waits outside with everyone']},
 {'type':'know','text':'A sudden gust sends {s}’s entire picnic flying. What gets rescued first?','options':['The food basket','Everyone’s phones','The picnic blanket','The group camera']},
 {'type':'know','text':'{s} receives six unrequested pizzas while the restaurant phone is busy. What now?','options':['Waits for the courier','Invites friends quickly','Freezes the boxes','Shares with neighbours']},
 {'type':'know','text':'The rented car left for {s} is bright pink with a giant advertisement. What happens?','options':['Drives it proudly','Demands a replacement','Pays for an upgrade','Photographs it first']},
 {'type':'know','text':'A parrot that insults visitors stays with {s} for the weekend. What is the plan?','options':['Teaches it compliments','Covers the cage','Invites an audience','Returns it early']},
 {'type':'know','text':'A stranger hands {s} the microphone at a wedding. How does the accidental speech begin?','options':['A short blessing','A harmless joke','A quick confession','A toast to dinner']},
 {'type':'know','text':'The shop alarm sounds after {s} has paid. What does {s} do first?','options':['Returns for a check','Raises the receipt','Freezes in place','Waits for security']},
]
bad=[
 {'type':'know','text':'{s} misses a flight and the suitcase disappears. What happens first?','options':['Calls the airline','Finds another flight','Buys clean clothes','Waits at the desk']},
 {'type':'know','text':'The plane leaves without {s}, and the luggage is gone. What is the first move?','options':['Calls the airport','Books a hotel','Replaces the clothes','Asks for compensation']},
 {'type':'know','text':'What matters most to {s} when making an important life decision?','options':['Money','Freedom','Friends','Career']},
 {'type':'know','text':'{s} gets a free Saturday with no plans. How is it spent?','options':['A day trip','A long lunch','It depends','A home project']},
 {'type':'know','text':'{s} needs help after the car breaks down. What happens first?','options':['Calls a friend','Calls a friend now','Walks to a garage','Orders a ride']},
]
pack=clean_pack(good+bad,'en')
texts={text for _,text,_ in pack}
assert len(pack)==9,pack
assert sum(('flight' in text or 'plane' in text) for text in texts)==1,texts
assert not any('plane leaves' in text for text in texts)
assert not any('matters most' in text for text in texts)
assert not any('free Saturday' in text for text in texts)
assert not any('car breaks down' in text for text in texts)
print('CONTENT_AI_FILTERS_WEAK_AND_DUPLICATE_OK')


hebrew_bad=[dict(item) for item in good]
hebrew_bad.append({'type':'know','text':'{s} מקבל/ת ארבע הזמנות לאותו ערב וצריך/ה לבחור אחת. לאן הולכים?','options':['למסיבת גג','לארוחה משפחתית','תלוי במצב','להופעה קטנה']})
hebrew_bad.extend([
 {'type':'know','text':'{s} מקבל/ת רובוט שמבצע כל בקשה מילולית מדי. מה המשימה הראשונה?','options':['להרים את האווירה','לסגור לי את הפינה','לעשות לי סדר בחיים','להביא קפה']},
 {'type':'know','text':'{s} בתפקיד קטן בסרט אבל צריך/ה לצעוק המלפפון ברח. מה עושים?','options':['צועק/ת חזק','לוחש/ת','מאלתר/ת','מסרב/ת']},
 {'type':'know','text':'{s} מגיע/ה עם חולצה זהה למארח שמבקש להחליף. מה עושים?','options':['מחליף/ה','מתווכח/ת','מצטלם/ת','הולך/ת']},
])
hebrew_pack=clean_pack(hebrew_bad,'he')
assert len(hebrew_pack)==8
assert not any('ארבע הזמנות' in text for _,text,_ in hebrew_pack)
assert not any('רובוט' in text or 'המלפפון' in text or 'חולצה זהה' in text for _,text,_ in hebrew_pack)
print('CONTENT_AI_FILTERS_HEBREW_DODGE_OK')


for language in SUPPORTED_LANGUAGES:
    variants=[last_resort(language,'Alex',index) for index in range(4)]
    assert len({text for text,_ in variants})==4,(language,variants)
    assert variants[0]==last_resort(language,'Alex')
    for text,options in variants:
        assert 'Alex' in text and '{name}' not in text,(language,text)
        assert len(options)==4 and all('{name}' not in option for option in options)
    copy=ui_copy(language)
    for field in ('chat_title','chat_placeholder','chat_send','chat_quick','reaction_heart','reaction_laugh','reaction_cry','reaction_mischief'):
        assert copy.get(field),(language,field)
print('CONTENT_EMERGENCY_POOL_AND_CHAT_LOCALES_OK')
