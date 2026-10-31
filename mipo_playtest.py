"""Reviewed, closed-choice content from the October group playtest."""
import re
import unicodedata

ROOM_TRAITS = [
 ('funny', 'הכי מצחיק', 'the funniest'),
 ('scared', 'הכי פחדן', 'the most easily scared'),
 ('responsible', 'הכי אחראי', 'the most responsible'),
 ('scattered', 'הכי מפוזר', 'the most absent-minded'),
 ('stubborn', 'הכי עקשן', 'the most stubborn'),
 ('late', 'הכי מאחר', 'the most often late'),
 ('competitive', 'הכי תחרותי', 'the most competitive'),
 ('dramatic', 'הכי דרמטי', 'the most dramatic'),
 ('secret', 'הכי טוב בשמירת סוד', 'the best at keeping a secret'),
 ('advice', 'נותן את העצות הכי טובות', 'the best at giving advice'),
 ('knows_me', 'מכיר אותו הכי טוב', 'the one who knows them best'),
 ('spends', 'מבזבז הכי הרבה', 'the biggest spender'),
 ('apology', 'הכי מתקשה להתנצל', 'the least likely to apologize first'),
 ('offended', 'נעלב הכי מהר', 'the most easily offended'),
 ('honest', 'הכי ישיר', 'the most direct'),
 ('organizer', 'הכי טוב בארגון תוכניות', 'the best at organizing plans'),
]

def room_pack(language='he', context=''):
 if language == 'he':
  pack=[('room',f'לדעת {{s}}, מי בחבורה {he}?',[]) for _,he,_ in ROOM_TRAITS]
  pack += [
   ('room','למי בחבורה {s} היה נותן לנהל לו את החיים לשבוע?',[]),
   ('room','למי בחבורה {s} היה מתקשר ראשון כשהוא צריך עזרה?',[]),
   ('room','עם מי בחבורה {s} הכי נוח לו לדבר על משהו אישי?',[]),
   ('room','על מי בחבורה {s} הכי סומך שיגיד לו את האמת?',[]),
   ('room','למי בחבורה {s} היה נותן לבחור לו דייט?',[]),
  ]
 elif language == 'en':
  pack=[('room',f'Who does {{s}} think is {en} in this group?',[]) for _,_,en in ROOM_TRAITS]
  pack += [
   ('room','Who would {s} trust to manage their life for a week?',[]),
   ('room','Who would {s} call first when they need help?',[]),
   ('room','Who does {s} feel most comfortable talking to about something personal?',[]),
   ('room','Who does {s} trust most to tell them the truth?',[]),
   ('room','Who would {s} trust to choose a date for them?',[]),
  ]
 else:return []
 if any(w in str(context).casefold() for w in ('family','משפחה','ילדים','children')):
  pack=[q for q in pack if 'דייט' not in q[1] and 'date for' not in q[1]]
 return pack

PERSONAL_HE = [
 ('know','מישהו פגע ב־{s} ואז כתב כאילו לא קרה כלום. איך מגיבים?',['מדברים על מה שקרה','עונים בקצרה ובקור','עונים כרגיל','לא עונים']),
 ('know','חבר מבקש מ־{s} דעה על בגד שלא מחמיא לו. מה אומרים?',['אומרים שלא מחמיא','מציעים בגד אחר','אומרים שנראה טוב','שואלים אם הוא מרוצה']),
 ('know','{s} מגלה שחברים נפגשו בלעדיו. מה הוא עושה קודם?',['שואל למה לא הוזמן','כותב משהו בקבוצה','מדבר עם חבר בפרטי','לא אומר כלום']),
 ('know','{s} כתב הודעה ולא קיבל תשובה, אבל ראה שהחבר מחובר. מה עכשיו?',['שולח עוד הודעה','מתקשר','מחכה לתשובה','מוחק את ההודעה']),
 ('know','מישהו מספר ליד {s} סיפור לא מדויק על ערב שהיה בו. מה עושים?',['מתקנים מול כולם','מתקנים אותו אחר כך','זורמים עם הסיפור','מוסיפים בצחוק גרסה משלהם']),
 ('know','חבר מבקש מ־{s} להלוות כסף ולא אומר מתי יחזיר. מה התגובה?',['מלווים בלי לשאול','קובעים מועד להחזרה','מלווים סכום קטן יותר','מסרבים להלוות']),
 ('know','{s} הפסיד במשחק וכולם חוגגים מולו. מה התגובה?',['מבקש משחק חוזר','צוחק על ההפסד','מתווכח על הכללים','מפרגן למנצח']),
 ('know','חבר מעיר ל־{s} שהוא מאחר תמיד. איך הוא מגיב?',['מודה שזה נכון','מסביר למה איחר הפעם','מחזיר הערה לחבר','צוחק ומעביר נושא']),
 ('know','{s} הזמין פחות מכולם והציעו לחלק את החשבון שווה. מה עושה?',['משלם שווה','מבקש לשלם לפי ההזמנה','מציע חשבונות נפרדים','מעיר על זה בצחוק']),
 ('know','חבר ביקש מ־{s} לשמור סוד ממש טוב. מה הכי קשה לו?',['לא לספר לבן הזוג','לא לרמוז לחבורה','לא לשאול עוד שאלות','לא להראות שהוא יודע']),
 ('know','{s} רואה תמונה קבוצתית שבה כולם יצאו טוב חוץ ממנו. מה עושה?',['מבקש צילום נוסף','מבקש שלא יעלו','מעלה עם בדיחה על עצמו','נותן לאחרים לפרסם']),
 ('know','{s} מקבל ביקורת שהוא לא מסכים איתה. מה קורה קודם?',['מבקש דוגמה','מסביר למה היא לא נכונה','שותק וחושב על זה','מחזיר ביקורת משלו']),
 ('know','החבורה בוחרת מסעדה ש־{s} לא אוהב. מה הוא עושה?',['מציע מקום אחר','מצטרף בכל זאת','מצטרף אחרי הארוחה','מנסה לשכנע חבר לתמוך בו']),
 ('know','חבר ביטל ל־{s} ברגע האחרון בפעם השלישית. מה הוא עושה?',['אומר שזה מפריע לו','מפסיק ליזום איתו','קובע איתו מחדש','מתרחק בלי להסביר']),
 ('know','{s} קנה משהו יקר ואז גילה שאפשר היה לשלם פחות. מה עושה?',['מנסה להחזיר','מבקש הפרש במחיר','מתבאס וממשיך הלאה','משכנע את עצמו שהקנייה שווה']),
 ('know','מישהו מעתיק רעיון של {s} ומקבל עליו מחמאות. מה התגובה?',['אומר שהרעיון שלו','מדבר איתו בפרטי','רומז על זה בצחוק','לא אומר אבל זוכר']),
 ('know','{s} קיבל הודעה ״אנחנו צריכים לדבר״. מה הוא עושה?',['מתקשר מיד','שואל על מה','משחזר מה אולי עשה','מחכה לשיחה בלי לשאול']),
 ('know','אחרי ויכוח, מה הכי יעזור ל־{s} להשלים?',['התנצלות מפורשת','שיחה רגועה','קצת זמן לבד','מחווה קטנה']),
 ('know','חבר מעלה על {s} בדיחה שפגעה בו. מה הוא עושה?',['אומר שנפגע מול כולם','מדבר איתו אחר כך','מחזיר בדיחה','צוחק למרות שנפגע']),
 ('know','{s} צריך לבחור: ערב מתוכנן מראש או ערב בלי תוכנית?',['הכול מתוכנן','קובעים רק מקום ראשון','בוחרים ברגע האחרון','נותנים לחבר להחליט']),
 ('know','בן משפחה שואל את {s} שאלה אישית מול כולם. מה התגובה?',['עונה בכנות','עונה בקצרה','מחזיר שאלה בצחוק','אומר שמעדיף לדבר בפרטי']),
 ('know','איזה הרגל של חבר הכי מפריע ל־{s}?',['איחורים','התעסקות בטלפון','ביטולים ברגע האחרון','קטיעה באמצע משפט']),
 ('know','איזו מחמאה הכי תשמח את {s}?',['אפשר לסמוך עליך','אתה מצחיק אותי','אתה מבין אותי','יש לך טעם מעולה']),
 ('know','באיזה נושא הכי קשה לשנות את דעתו של {s}?',['כסף','זוגיות','חברים','איך נכון לעשות דברים']),
]

def editorial_ok(q, language='he'):
 if not isinstance(q,(tuple,list)) or len(q)!=3:return False
 typ,text,opts=q
 if typ not in ('know','room') or not isinstance(text,str) or not text.strip():return False
 if not isinstance(opts,(tuple,list)) or not all(isinstance(o,str) and o.strip() for o in opts):return False
 if language=='he' and re.search(r'[\u0600-\u06ff]',text+' '.join(map(str,opts))):return False
 if typ=='room':return True
 if not isinstance(opts,(tuple,list)) or not 2<=len(opts)<=4:return False
 normal=lambda s:' '.join(unicodedata.normalize('NFKC',str(s)).casefold().split())
 if len({normal(o) for o in opts})!=len(opts):return False
 # Filler choices that evade rather than answer the decision.
 return not any(normal(o) in ('תלוי','תלוי במצב','איזון','שילוב','מסרב/ת לבחור','משהו אחר','both','it depends','something else') for o in opts)

def canonical_key(text):
 """Stable identities for short trait questions; different traits remain distinct."""
 clean=lambda s:re.sub(r'[^\w{}]+',' ',s.casefold()).strip()
 normalized=clean(text)
 for language in ('he','en'):
  for i,(_,template,_) in enumerate(room_pack(language)):
   if normalized==clean(template):return 'crew-choice:'+str(i)
 # Existing and newly worded versions of this scenario share one history key.
 if ('חופשה' in text and ('הכרטיס השני' in text or 'אדם אחד מהחבורה' in text)):
  return 'scenario:holiday-companion'
 return None
