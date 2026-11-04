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
   ('room','למי בחבורה {s} הכי מתקשה להגיד לא?',[]),
   ('room','למי בחבורה {s} היה מספר ראשון על חדשות טובות?',[]),
   ('room','למי בחבורה {s} היה נותן לנהל לו את הכסף?',[]),
   ('room','מי לדעת {s} תמיד חייב להגיד את המילה האחרונה?',[]),
  ]
 elif language == 'en':
  pack=[('room',f'Who does {{s}} think is {en} in this group?',[]) for _,_,en in ROOM_TRAITS]
  pack += [
   ('room','Who would {s} trust to manage their life for a week?',[]),
   ('room','Who would {s} call first when they need help?',[]),
   ('room','Who does {s} feel most comfortable talking to about something personal?',[]),
   ('room','Who does {s} trust most to tell them the truth?',[]),
   ('room','Who would {s} trust to choose a date for them?',[]),
   ('room','Who in this group does {s} find hardest to say no to?',[]),
   ('room','Who in this group would {s} tell good news to first?',[]),
   ('room','Who in this group would {s} trust to manage their money?',[]),
   ('room','Who does {s} think always needs to have the last word?',[]),
  ]
 else:return []
 if any(w in str(context).casefold() for w in ('family','משפחה','ילדים','children')):
  pack=[q for q in pack if 'דייט' not in q[1] and 'date for' not in q[1]]
 return pack

PERSONAL_HE = [
 ('know','מישהו פגע ב־{s} ואז כתב כאילו לא קרה כלום. איך מגיבים?',['מדברים על מה שקרה','עונים בקצרה ובקור','עונים כרגיל','לא עונים']),
 ('know','חבר מודד חולצה שלא מחמיאה לו ושואל את {s} איך היא נראית עליו. מה תהיה התגובה של {s}?',['לומר בעדינות שהחולצה לא מחמיאה','להציע למדוד חולצה אחרת','להגיד שהיא נראית טוב','לשאול אם הוא אוהב אותה']),
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
 return semantic_family(text)

# Each reviewed card has one decision, four answers, and an editorial identity.
# Identity is narrower than a topic: two money cards need not be the same dilemma.
REVIEWED = [
 ('habits',2,'friend-friction','מה יותר מפריע ל־{s} אצל חבר?',['מאחר בלי לעדכן','מבטל ברגע האחרון','קוטע באמצע משפט','חייב תמיד להיות צודק'], 'What bothers {s} most in a friend?',['Being late without a message','Cancelling at the last minute','Interrupting mid-sentence','Always having to be right']),
 ('trust',2,'good-news-reaction','{s} מספר לחבר חדשות טובות. איזו תגובה הכי תאכזב אותו?',['מחליף נושא מיד','מתחיל לדבר על עצמו','מסביר למה זה לא כזה הישג','אומר יפה בלי להרים מבט'], '{s} shares good news with a friend. Which response would disappoint them most?',['Changing the subject','Making it about themselves','Playing down the achievement','Saying nice without looking up']),
 ('boundaries',2,'borrowed-item','חבר מחזיר ל־{s} משהו ששאל, והוא פגום. מה {s} מבקש?',['שיתקן אותו','שיקנה חדש','שישלם את שווי הנזק','לא מבקש פיצוי'], 'A friend returns something damaged to {s}. What do they ask for?',['Have it repaired','Buy a replacement','Pay for the damage','Ask for no compensation']),
 ('honesty',2,'private-screenshot','חבר שולח ל־{s} צילום מסך של שיחה פרטית עם חבר אחר. מה התגובה?',['קורא ומגיב על השיחה','שואל אם מותר לשתף אותה','מבקש שלא ישלח עוד צילומים','מוחק בלי לקרוא'], 'A friend sends {s} a screenshot of another friend’s private chat. What happens?',['Read it and comment','Ask if they had permission','Ask not to receive more','Delete it without reading']),
 ('money',2,'birthday-budget','מתכננים מתנה לחבר בסכום שגבוה מהתקציב של {s}. מה עושה?',['אומר מה התקציב שלו','מציע מתנה זולה יותר','קונה מתנה בנפרד','מצטרף למרות המחיר'], 'A group gift costs more than {s} can budget. What do they do?',['State their budget','Suggest a cheaper gift','Give a separate gift','Join in despite the cost']),
 ('trust',3,'friend-ex','חבר מתחיל לצאת עם האקס של {s}. מה הכי חשוב ל־{s}?',['שישמע על זה מהחבר','שידברו לפני הדייט הראשון','שלא יביא אותו למפגשי החבורה','שלא ידברו איתו על הקשר'], 'A friend starts dating {s}’s ex. What matters most to {s}?',['Hear it from the friend','Talk before the first date','Keep the ex out of group plans','Not hear about the relationship']),
 ('honesty',2,'apology-style','איזו התנצלות הכי תעצבן את {s}?',['מצטער אם נפגעת','סליחה אבל גם אתה אשם','כבר התנצלתי מה עוד רצית','זה היה בצחוק'], 'Which apology would annoy {s} most?',['Sorry if you were offended','Sorry, but you did it too','I said sorry, what else do you want','It was only a joke']),
 ('plans',2,'host-overstay','כבר מאוחר והאורחים אצל {s} לא הולכים. מה עושה?',['אומר שהוא הולך לישון','מתחיל לסדר את הבית','מציע לקבוע שוב בקרוב','ממשיך לארח עד שילכו'], 'It is late and {s}’s guests are not leaving. What do they do?',['Say they are going to bed','Start tidying up','Suggest meeting again soon','Keep hosting until they leave']),
 ('plans',1,'host-plans','{s} מארח הערב והחברים שואלים מה להביא. מה הוא מבקש?',['משהו לאכול','משהו לשתות','שיבואו בזמן','שלא יביאו כלום'], '{s} is hosting tonight. What do they ask friends to bring?',['Something to eat','Something to drink','Just arrive on time','Nothing at all']),
 ('habits',1,'packing','כולם כבר מוכנים לצאת. מה הכי סביר שמעכב את {s}?',['מחפש את המפתחות','מחליף בגדים שוב','מסיים משהו בטלפון','בודק שלא שכח כלום'], 'Everyone is ready to leave. What is most likely holding {s} up?',['Looking for their keys','Changing clothes again','Finishing something on their phone','Checking they packed everything']),
 ('food',1,'restaurant-choice','{s} חוזר למסעדה שהוא אוהב. מה הוא מזמין?',['את המנה הקבועה','מנה חדשה לגמרי','מה שהמלצר ממליץ','כמה מנות לחלוק'], '{s} returns to a favourite restaurant. What do they order?',['Their usual dish','Something completely new','The waiter’s recommendation','Several dishes to share']),
 ('habits',1,'game-competition','באמצע משחק, {s} מגלה שחבר לא הבין כלל חשוב. מה עושה?',['עוצרים ומסבירים','מתחילים את הסיבוב מחדש','ממשיכים ומסבירים בסוף','נותנים לו הזדמנות נוספת'], 'Mid-game, {s} notices a friend misunderstood a rule. What do they do?',['Stop and explain','Restart the round','Explain after this round','Give them another chance']),
 ('plans',1,'party-arrival','{s} מגיע למסיבה ומכיר רק את המארח. מה הוא עושה קודם?',['נשאר ליד המארח','מציג את עצמו למישהו','הולך להביא שתייה','שולח לחבר שיבוא'], '{s} arrives at a party knowing only the host. What do they do first?',['Stay near the host','Introduce themselves to someone','Go and get a drink','Text a friend to come']),
 ('food',1,'last-slice','נשארה פרוסת פיצה אחת ו־{s} עדיין רעב. מה עושה?',['לוקח אותה','שואל מי רוצה','מציע לחלוק אותה','מחכה שמישהו יציע לו'], 'One pizza slice is left and {s} is hungry. What do they do?',['Take the slice','Ask who wants it','Offer to split it','Wait to be offered it']),
 ('money',2,'unpaid-debt','חבר חייב ל־{s} כסף ושכח להחזיר. מה הוא עושה?',['מזכיר לו ישירות','שולח בקשת תשלום','מעלה את זה בצחוק','מחכה שייזכר לבד'], 'A friend forgot to repay {s}. What do they do?',['Remind them directly','Send a payment request','Mention it as a joke','Wait for them to remember']),
 ('trust',2,'unsolicited-advice','{s} מספר לחבר על יום קשה ומקבל עצות שלא ביקש. מה אומר?',['רק רציתי שתשמע אותי','תודה, אחשוב על זה','מסביר למה זה לא יעזור','משנה את נושא השיחה'], '{s} vents about a hard day and gets unwanted advice. What do they say?',['I just needed you to listen','Thanks, I’ll think about it','Explain why it won’t help','Change the subject']),
 ('messages',2,'group-disagreement','בקבוצה מציעים תוכנית ש־{s} לא רוצה, וכולם מסכימים. מה עושה?',['אומר שזה לא מתאים לו','מציע חלופה בקבוצה','מדבר עם חבר בפרטי','מסכים ומצטרף'], 'Everyone agrees on a group plan that {s} dislikes. What do they do?',['Say it doesn’t suit them','Suggest another plan','Message one friend privately','Agree and join in']),
 ('boundaries',2,'uninvited-guest','חבר מבקש להביא עוד מישהו לארוחה קטנה אצל {s}. מה התגובה?',['בטח, שיבוא','שואל קודם מי זה','מסכים רק הפעם','מבקש להישאר בהרכב המקורי'], 'A friend asks to bring someone extra to dinner at {s}’s. What is the response?',['Of course, bring them','Ask who it is first','Agree just this once','Keep the original guest list']),
 ('habits',2,'shared-space','{s} חולק חדר בחופשה עם חבר מבולגן. מה הוא עושה?',['מסדר גם בשבילו','מבקש ממנו לסדר','קובע אזור נפרד לכל אחד','מתעלם מהבלגן'], '{s} shares a holiday room with a messy friend. What do they do?',['Tidy up for both','Ask them to tidy up','Agree on separate spaces','Ignore the mess']),
 ('honesty',2,'honest-feedback','חבר מבקש מ־{s} ביקורת כנה על משהו שהכין. איך עונים?',['אומרים ישר מה לא עובד','מתחילים במה שכן טוב','שואלים כמה כנות הוא רוצה','מציעים שינוי אחד קטן'], 'A friend asks {s} for honest feedback on their work. How do they respond?',['Say what isn’t working','Start with what works','Ask how honest to be','Suggest one small change']),
 ('trust',3,'public-support','חבר מתווכח מול כולם, ו־{s} חושב שהוא טועה. מה עושה?',['אומר שהוא לא מסכים','תומך בו ומדבר איתו אחר כך','מנסה להרגיע את כולם','לא מתערב בוויכוח'], 'A friend argues in front of everyone, but {s} thinks they’re wrong. What happens?',['Say they disagree','Back them, then talk privately','Try to calm everyone down','Stay out of the argument']),
 ('boundaries',3,'phone-privacy','בן הזוג מבקש לראות הודעה פרטית בטלפון של {s}. מה התגובה?',['מראה את ההודעה','מסביר מה כתוב בלי להראות','שואל למה הוא רוצה לראות','אומר שזו שיחה פרטית'], '{s}’s partner asks to read a private message on their phone. How do they respond?',['Show the message','Explain it without showing it','Ask why they want to see','Say the conversation is private']),
 ('honesty',3,'friend-secret','{s} מגלה שחבר הסתיר ממנו משהו שכולם כבר ידעו. מה הכי מפריע לו?',['שלא סמכו עליו','שהאחרים ידעו לפניו','שלא סיפרו לו ישירות','שזה נשמר בסוד בכלל'], '{s} discovers a friend told everyone a secret except them. What bothers them most?',['Not being trusted','Being the last to know','Not hearing it directly','Keeping it secret at all']),
 ('trust',3,'changed-friendship','{s} מרגיש שרק הוא יוזם מפגשים עם חבר. מה הוא עושה?',['מדבר איתו על זה','מפסיק ליזום ובודק מה יקרה','מציע מפגש אחרון','ממשיך ליזום כרגיל'], '{s} feels they always initiate plans with a friend. What do they do?',['Talk to them about it','Stop initiating and see','Suggest one last meetup','Keep making the plans']),
 ('boundaries',3,'personal-joke','חבר משתמש במשהו אישי של {s} כדי להצחיק את החבורה. מה התגובה?',['מבקש לעצור מול כולם','לוקח אותו לשיחה בפרטי','מחזיר לו באותה מטבע','צוחק אבל מתרחק ממנו'], 'A friend uses something private about {s} as a group joke. How do they react?',['Ask them to stop publicly','Take them aside privately','Make a joke back at them','Laugh but pull away']),
 ('honesty',3,'unpopular-opinion','ל־{s} יש דעה שונה משל כל החבורה. מתי הוא אומר אותה?',['מיד, גם אם יתווכחו','רק אם שואלים אותו','אומר לחבר אחד אחר כך','מעדיף להשאיר אותה לעצמו'], '{s} disagrees with everyone in the group. When do they say so?',['Immediately, even if they argue','Only if someone asks','Tell one friend later','Keep it to themselves']),
]

# Metadata for the existing 24 cards, in their original order.
_BASE_META=[
 ('trust',3,'hurt-then-normal'),('honesty',2,'unflattering-clothes'),('trust',3,'excluded-meetup'),
 ('messages',2,'ignored-message'),('honesty',2,'inaccurate-story'),('money',2,'lending-money'),
 ('habits',1,'losing-game'),('habits',2,'called-out-late'),('money',2,'split-bill'),
 ('trust',3,'keeping-secret'),('habits',1,'group-photo'),('honesty',2,'receiving-criticism'),
 ('food',1,'disliked-restaurant'),('plans',2,'repeated-cancellation'),('money',2,'price-regret'),
 ('honesty',3,'stolen-credit'),('messages',2,'need-to-talk'),('trust',3,'making-up'),
 ('boundaries',3,'hurtful-joke'),('plans',1,'planned-evening'),('boundaries',2,'personal-question'),
 ('habits',2,'annoying-habit'),('trust',1,'favourite-compliment'),('honesty',2,'stubborn-topic')]
_PERSONAL_PROFILES=list(zip(PERSONAL_HE,_BASE_META))
PERSONAL_HE += [('know',q[3],q[4]) for q in REVIEWED]
PERSONAL_EN = [('know',q[5],q[6]) for q in REVIEWED]
_PERSONAL_PROFILES += [(('know',q[3],q[4]),q[:3]) for q in REVIEWED]
_PERSONAL_PROFILES += [(('know',q[5],q[6]),q[:3]) for q in REVIEWED]

def _norm(text):
 return re.sub(r'[^\w{}]+',' ',unicodedata.normalize('NFKC',str(text)).casefold()).strip()
_PROFILES=[(re.compile(re.escape(_norm(q[1])).replace(r'\{s\}',r'.+?')),meta) for q,meta in _PERSONAL_PROFILES]
_META={key:(category,depth) for _,(category,depth,key) in _PERSONAL_PROFILES}
# Explicit aliases catch changed wording, not just different player names.
_SCENARIOS=[
 ('annoying-habit',r'(איזה הרגל של חבר|מה יותר מפריע ל־|What bothers .+ most in a friend)'),
 ('ignored-message',r'(ראה.*הודעה.*לא ענה|לא קיבל תשובה|לא עונה להודע|לא עונה להודעה|ignores? .*message|message.*no reply|read.*message.*reply)'),
 ('lending-money',r'(להלוות כסף|מלווה כסף|lend.*money|loan.*friend)'),
 ('unpaid-debt',r'(חייב.*כסף.*שכח|forgot.*repay|forgot.*pay.*back)'),
 ('split-bill',r'(לחלק.*חשבון.*שווה|חשבון.*לחלק.*שווה|split.*bill|bill.*equally|חשבון משותף)'),
 ('group-photo',r'(תמונה קבוצתית.*כולם|group photo|unflattering photo)'),
 ('stolen-credit',r'(מעתיק רעיון|לוקח.*קרדיט|takes?.*credit|steals?.*idea)'),
 ('personal-joke',r'(משהו אישי.*להצחיק|something private.*joke)'),
 ('excluded-meetup',r'(חברים נפגשו בלעד|friends.*met.*without|friends.*didn.*invite)'),
 ('repeated-cancellation',r'(ביטל.*פעם השלישית|cancel.*third time)'),
]

def semantic_family(text):
 text=str(text)
 if text.startswith('scenario:'):return text
 for key,pattern in _SCENARIOS:
  if re.search(pattern,text,re.I):return 'scenario:'+key
 normalized=_norm(text)
 for pattern,(_,_,key) in _PROFILES:
  if pattern.fullmatch(normalized):return 'scenario:'+key
 return None

def content_profile(text):
 """Return topic and intimacy, for pacing rather than personality classification."""
 text=str(text)
 concept=semantic_family(text)
 if concept and concept[9:] in _META:return _META[concept[9:]]
 normalized=_norm(text)
 for language in ('he','en'):
  for i,q in enumerate(room_pack(language)):
   pattern=re.escape(_norm(q[1])).replace(r'\{s\}',r'.+?')
   if re.fullmatch(pattern,normalized):return ('crew',1 if i in (0,1,2,3,5,6,15) else 2 if i in (4,7,9,11,16,17) else 3)
 if re.search(r'(אינטימ|סקס|משיכה|דייט|dating|sex|intimacy|attraction)',text,re.I):return ('dating',3)
 for category,pattern in [('messages',r'הודע|וואטסאפ|message|text|chat'),('money',r'כסף|חשבון|קנה|קונה|money|bill|buy|spend'),('food',r'מסעד|ארוח|אוכל|food|dinner|restaurant'),('plans',r'תוכנית|חופשה|טיול|plans|holiday|trip'),('trust',r'סוד|סומך|secret|trust')]:
  if re.search(pattern,text,re.I):return category,2
 return 'everyday',2

def paced_candidates(cards,round_no,total,history,seed):
 """Deterministic within a round; history changes only when the host advances."""
 if not cards:return []
 phase=1 if round_no<max(2,int(total*.25)) else 2 if round_no<max(3,int(total*.65)) else 3
 recent=[content_profile(e.get('question',''))[0] for e in history[-2:]]
 rotated=cards[seed%len(cards):]+cards[:seed%len(cards)]
 def rank(q):
  category,depth=content_profile(q[1])
  reviewed=bool(semantic_family(q[1])) or q[0]=='room'
  return (max(0,depth-phase),recent.count(category),not reviewed,abs(depth-phase))
 return sorted(rotated,key=rank)
