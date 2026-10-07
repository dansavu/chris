"""Audioghid pentru „Mein Deutschheft" — o pistă MP3 per pagină (audio/01.mp3 … 20.mp3).

Două voci (Gemini TTS multi-speaker): Fernanda (română) + Eric (spune cuvintele germane cu pronunție nativă).
Cheia API: variabila de mediu GEMINI_API_KEY sau se cere în terminal (nu se afișează).
Utilizare:  python genereaza_audio.py [--list] [--force] [01 05 ...]
"""
import base64, getpass, json, os, re, subprocess, sys, time, wave
import truststore
truststore.inject_into_ssl()
import urllib.request, urllib.error

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
PREFERRED = ["3.8", "3.5", "3.1", "3.0", "2.5"]
VOICES = {"Fernanda": "Erinome", "Eric": "Puck"}
P = "[long pause]"

DIRECTOR = f"""Director's notes — audioghid pentru un băiat de 7 ani (Chris) care învață primele cuvinte în germană.
Fernanda: o furnică mică, blândă, caldă și veselă; vorbește în limba română, rar, clar, cu zâmbet în voce.
Eric: robotul prietenos al lui Chris, entuziast și jucăuș. Cuvintele și propozițiile GERMANE le spune cu pronunție germană nativă, perfectă, rar și foarte clar, ca un profesor pentru copii. Puținele fraze în română le spune normal, în română.
Când apare {P}: tăcere de aproximativ 3 secunde, ca să poată repeta copilul. Nu citi niciodată tagurile sau numele vorbitorilor.

"""

T = {}

T["01"] = f"""Fernanda: Bună, Chris! Eu sunt Fernanda, furnica ta cu ochelari rotunzi. Tocmai am aterizat cu avionul meu de hârtie chiar pe caietul tău nou! Uite ce scrie pe copertă:
Eric: Mein Deutschheft!
Fernanda: Adică: caietul meu de germană. Eric, spune încă o dată, rar!
Eric: Mein... Deutsch... heft.
Fernanda: Spune și tu! {P} Bravo! În fiecare marți vine Elena și vă jucați în germană. Iar în celelalte zile, eu și Eric te ajutăm cu caietul ăsta. Eric a învățat germana ca un adevărat robot poliglot: el spune cuvintele nemțești, iar tu le repeți după el.
Eric: Hallo, Chris! Ich bin Eric!
Fernanda: Acum ia un creion și scrie-ți numele jos, pe copertă, unde scrie „Name". {P} Gata? Atunci întoarce pagina!"""

T["02"] = f"""Fernanda: Pe pagina asta sunt toți prietenii tăi. În germană, când prezinți pe cineva, spui „Das ist" — adică „acesta este". Ascultă-l pe Eric și arată cu degetul fiecare prieten.
Eric: Das ist Fernanda. Sie ist eine Ameise.
Fernanda: Asta sunt eu! O furnică: eine Ameise. Repetă: eine Ameise. {P}
Eric: Das ist Eric. Er ist mein Roboter. Hm... asta trebuie să o spui tu, Chris!
Fernanda: Da! Spune tu: Das ist Eric! {P} Super!
Eric: Das ist Clara. Sie ist meine Freundin.
Eric: Das ist Pip. Er ist ein Pinguin.
Eric: Das sind Uno und Deca. Eins und zehn!
Eric: Das ist Milo. Er ist ein kleiner Roboter.
Eric: Melba ist ein Alpaka. Mello ist ein Hund. Malva ist eine Maus.
Eric: Das sind Leo und Mikey, die Ninja-Schildkröten. Und das sind die Mimigs: Millie, Miguel und Mike.
Fernanda: Și ultima, jos în dreapta... e Elena! Sie spricht Deutsch — ea vorbește germană. Acum joacă-te tu: arată un prieten și spune „Das ist" și numele lui. Începe cu Pip! {P} Foarte bine! Mai arată unul! {P}"""

T["03"] = f"""Fernanda: Lecția unu: Hallo! Adică: salut! Ascultă și repetă după Eric. După fiecare cuvânt ai timp să-l spui și tu.
Eric: Hallo! {P}
Fernanda: Salut!
Eric: Guten Morgen! {P}
Fernanda: Bună dimineața! Se spune dimineața, când te trezești.
Eric: Guten Tag! {P}
Fernanda: Bună ziua!
Eric: Tschüss! {P}
Fernanda: Pa! Asta strigă Pip când pleacă cu avionul lui. Atenție la sunetul ü, cu două puncte: îl știi din franceză, ca în „tu".
Eric: Danke! {P}
Fernanda: Mulțumesc!
Eric: Bitte! {P}
Fernanda: Te rog. Sau: poftim.
Eric: Ja! {P} Nein! {P}
Fernanda: Da... și nu. Și acum cea mai importantă întrebare. Când vrei să afli cum îl cheamă pe cineva, întrebi:
Eric: Wie heißt du? {P}
Fernanda: Cum te cheamă? Iar tu răspunzi: Ich heiße Chris. Hai să încercăm. Eric, întreabă-l!
Eric: Hallo! Wie heißt du? {P}
Fernanda: Super! Acum tu îl întrebi pe Eric. {P}
Eric: Ich heiße Eric! Danke!
Fernanda: Marți, când vine Elena, spune-i tu primul: Hallo, Elena! Wie heißt du? O să se bucure tare!"""

T["04"] = f"""Fernanda: Exercițiile lecției unu. Exercițiul unu: Verbinde! Adică: unește. În stânga sunt imagini, în dreapta cuvinte. Trage o linie de la fiecare punct la cuvântul potrivit.
Fernanda: Soarele care răsare... ce spui dimineața? {P}
Eric: Guten Morgen!
Fernanda: Pip face cu aripa, pleacă... ce spune? {P}
Eric: Tschüss!
Fernanda: Primești un cadou. Ce spui? {P}
Eric: Danke!
Fernanda: Și degetul mare în sus? {P}
Eric: Ja!
Fernanda: Exercițiul doi: Schreib nach! Scrie peste literele gri. Întâi: Hallo.
Eric: Hallo.
Fernanda: Apoi: Tschüss. Nu uita cele două puncte de pe ü!
Eric: Tschüss.
Fernanda: Exercițiul trei: Wer bist du? Cine ești tu? În balon, după „Ich heiße", scrie-ți numele. Apoi desenează-te în pătrat. Și spune tare:
Eric: Ich heiße...
Fernanda: {P} Perfect! Când ai terminat totul, spui:
Eric: Fertig!
Fernanda: Adică: gata! Colorează steaua din colț. Ai terminat prima lecție!"""

T["05"] = f"""Fernanda: Lecția doi: Die Zahlen — numerele. Uno și Deca, roboții tăi de la matematică, au venit să numere cu noi. Numără cu Eric, pe degete!
Eric: eins {P} zwei {P} drei {P} vier {P} fünf {P}
Fernanda: O mână întreagă! Continuăm cu cealaltă.
Eric: sechs {P} sieben {P} acht {P} neun {P} zehn! {P}
Fernanda: Zece... ca Deca! Atenție la trei numere care sună altfel decât se scriu: zwei se spune „țvai", vier se spune „fir", iar sechs se spune „zecs". Acum toate, mai repede, împreună:
Eric: eins, zwei, drei, vier, fünf, sechs, sieben, acht, neun, zehn!
Fernanda: Când vrei să întrebi „câte?", spui:
Eric: Wie viele? {P}
Fernanda: Iar Elena poate să-ți spună: Zeig mir drei Finger! Arată-mi trei degete!
Eric: Zeig mir drei Finger! {P} Zeig mir fünf Finger! {P}
Fernanda: Bravo! Și acum o numărătoare pe care o știu toți copiii din Germania. Ascult-o o dată:
Eric: Eins, zwei — Polizei. Drei, vier — Offizier. Fünf, sechs — alte Hex. Sieben, acht — gute Nacht. Neun, zehn — auf Wiedersehen!
Fernanda: Polizei e poliția, Offizier e un ofițer, alte Hex e o vrăjitoare bătrână, gute Nacht înseamnă noapte bună, iar auf Wiedersehen înseamnă la revedere. Acum spune-o și tu cu Eric, bucată cu bucată.
Eric: Eins, zwei — Polizei. {P} Drei, vier — Offizier. {P} Fünf, sechs — alte Hex. {P} Sieben, acht — gute Nacht. {P} Neun, zehn — auf Wiedersehen! {P}
Fernanda: Minunat! Marți poți să i-o spui Elenei!"""

T["06"] = f"""Fernanda: Exercițiile cu numere. Exercițiul unu: Zähle und kreise ein! Numără și încercuiește cuvântul corect. Numără feliile de pizza, în germană! {P}
Eric: drei!
Fernanda: Încercuiește drei. Acum pinguinii. {P}
Eric: fünf!
Fernanda: Mingile de tenis. Sunt mai multe, numără atent. {P}
Eric: sieben!
Fernanda: Și furnicile, ca mine. {P}
Eric: zwei!
Fernanda: Exercițiul doi: Male vier Unos aus! Colorează cu galben patru roboței Uno. Doar patru! Numără în germană în timp ce colorezi: eins, zwei, drei, vier. {P}
Fernanda: Exercițiul trei: Rechne mit Deca! Socotește cu Deca. Eric îți citește socotelile, tu spui răspunsul în germană și îl scrii.
Eric: zwei plus drei... {P}
Fernanda: fünf! Scrie cinci.
Eric: vier plus vier... {P}
Fernanda: acht!
Eric: fünf plus fünf... {P}
Fernanda: zehn!
Eric: zehn minus eins... {P}
Fernanda: neun! Ești un campion la mate și în germană! Colorează steaua!"""

T["07"] = f"""Fernanda: Lecția trei: Die Farben — culorile. Fiecare prieten are culoarea lui. Arată cu degetul și repetă după Eric.
Eric: gelb {P}
Fernanda: galben, ca Uno.
Eric: blau {P}
Fernanda: albastru, ca Deca.
Eric: rot {P}
Fernanda: roșu, ca Centa.
Eric: grün {P}
Fernanda: verde, ca Milo.
Eric: lila {P}
Fernanda: mov, ca Multiplo.
Eric: orange {P}
Fernanda: portocaliu, ca masca lui Mikey.
Eric: rosa {P}
Fernanda: roz, ca Simka.
Eric: weiß {P}
Fernanda: alb, ca Melba.
Eric: schwarz {P}
Fernanda: negru, ca Pip.
Eric: braun {P}
Fernanda: maro, ca mine!
Eric: silber {P}
Fernanda: argintiu, ca Mila.
Eric: gold {P}
Fernanda: auriu, ca Mello. Acum o întrebare. În germană întrebi „ce culoare are?" așa:
Eric: Welche Farbe hat Deca? {P}
Fernanda: Blau! Și răspunsul întreg este:
Eric: Deca ist blau. {P} Welche Farbe hat Uno? {P}
Fernanda: Uno ist gelb! Uită-te prin cameră: ce vezi care e rot? Arată și spune: rot! {P}"""

T["08"] = f"""Fernanda: Exercițiile cu culori. Pregătește creioanele colorate! Exercițiul unu: Male die Masken aus! Colorează măștile țestoaselor. Pielea lor e grün, verde.
Eric: Leonardo — blau. {P} Raphael — rot. {P} Donatello — lila. {P} Michelangelo — orange. {P}
Fernanda: Exercițiul doi: Male die Roboter aus! Colorează roboții după cuvântul de sub ei.
Eric: Uno — gelb. {P} Deca — blau. {P} Centa — rot. {P} Milo — grün. {P} Multiplo — lila. {P}
Fernanda: Exercițiul trei: Und du? Și tu? Care e culoarea ta preferată? În germană spui:
Eric: Meine Lieblingsfarbe ist blau!
Fernanda: Asta e a lui Eric. Tu care o ai? Spune tare! {P} Scrie-o pe linie și colorează pata cu ea. Apoi colorează steaua!"""

T["09"] = f"""Fernanda: Lecția patru: Die Tiere — animalele. Înainte de fiecare animal auzi un cuvințel mic: der, die sau das. E ca o pălărie pe care o poartă cuvântul. Învață cuvântul împreună cu pălăria lui!
Eric: die Ameise {P}
Fernanda: furnica — adică eu!
Eric: der Pinguin {P}
Fernanda: pinguinul, ca Pip.
Eric: die Robbe {P}
Fernanda: foca, prietena lui Pip de pe gheață.
Eric: der Hund {P}
Fernanda: câinele, ca Mello.
Eric: die Maus {P}
Fernanda: șoricelul, ca Malva.
Eric: das Alpaka {P}
Fernanda: alpaca, ca Melba.
Eric: die Schildkröte {P}
Fernanda: țestoasa. E un cuvânt lung, încă o dată rar:
Eric: Schild... kröte. {P}
Eric: die Ratte {P}
Fernanda: șobolanul, ca maestrul Splinter. Acum ascultă o propoziție:
Eric: Das ist Pip. Pip ist ein Pinguin. {P}
Fernanda: Și ce fac animalele? În germană câinele nu face ham-ham!
Eric: Der Hund macht: Wau wau! {P}
Eric: Die Maus macht: Piep piep! {P}
Eric: Und die Ameise macht... psst!
Fernanda: Da, furnicile sunt foarte liniștite. Psst!"""

T["10"] = f"""Fernanda: Exercițiile cu animale. Exercițiul unu: Verbinde! Unește fiecare animal cu numele lui. Ascultă-l pe Eric și caută.
Eric: die Maus {P} der Pinguin {P} das Alpaka {P} der Hund {P}
Fernanda: Exercițiul doi: Wer bin ich? Cine sunt eu? Eric citește o ghicitoare, tu încercuiești răspunsul.
Eric: Ich bin klein. Ich habe eine Brille. Ich fliege! Wer bin ich? {P}
Fernanda: Sunt mică, am ochelari și zbor... Sunt eu, Fernanda!
Eric: Ich bin groß und weiß. Ich passe auf. Wer bin ich? {P}
Fernanda: Mare și albă, și are grijă de toți... Melba!
Eric: Ich wohne am Südpol. Ich bin schwarz und weiß. Wer bin ich? {P}
Fernanda: Locuiește la Polul Sud, e alb cu negru... Pip!
Fernanda: Exercițiul trei: Mein Lieblingstier. Animalul tău preferat. Eric, al tău care e?
Eric: Mein Lieblingstier ist der Hund! Wau wau!
Fernanda: Și al tău, Chris? Spune tare: Mein Lieblingstier ist... {P} Scrie-l pe linie și desenează-l în pătrat. La final, colorează steaua!"""

T["11"] = f"""Fernanda: Lecția cinci: Familie und Freunde — familia și prietenii. Uite-l pe Chris cu mama și tata.
Eric: die Mama {P} der Papa {P} ich {P}
Fernanda: Ich înseamnă eu. Acum toată propoziția:
Eric: Das ist meine Mama. {P} Das ist mein Papa. {P} Und das bin ich! {P}
Fernanda: Acum prietenii.
Eric: die Freundin {P}
Fernanda: prietena, ca Clara.
Eric: der Freund {P}
Fernanda: prietenul, ca Nolik.
Eric: der Roboter {P} Das bin ich!
Fernanda: Și familia Mimigs de pe planeta Mimondo. Millie e cea mai mare.
Eric: Millie ist die Schwester. Sie ist elf. {P}
Fernanda: Schwester înseamnă soră. Elf înseamnă unsprezece.
Eric: Miguel ist der Bruder. Er ist acht. {P}
Fernanda: Bruder înseamnă frate.
Eric: Mike ist der kleine Bruder. Er ist fünf. {P}
Fernanda: Fratele cel mic. Și acum întrebarea pentru tine:
Eric: Wie alt bist du? {P}
Fernanda: Câți ani ai? Tu răspunzi:
Eric: Ich bin sieben Jahre alt.
Fernanda: Spune și tu! {P} Perfect!"""

T["12"] = f"""Fernanda: Exercițiile lecției cinci. Exercițiul unu: Wie alt? Câți ani are fiecare? Unește.
Eric: Mike ist fünf. {P} Millie ist elf. {P} Miguel ist acht. {P}
Fernanda: Exercițiul doi: tortul tău de ziua ta. Scrie pe linie câți ani ai, și spune tare:
Eric: Ich bin... {P}
Fernanda: Sieben Jahre alt! Acum desenează pe tort șapte lumânări și numără-le în germană: eins, zwei, drei, vier, fünf, sechs, sieben! {P}
Fernanda: Exercițiul trei: Meine Familie. Desenează-ți familia în chenar: pe mama, pe tata, pe tine... poate și pe Eric! Apoi scrie jos: Das ist... și cine e. Când îi arăți desenul Elenei, spune-i:
Eric: Das ist meine Mama. Das ist mein Papa. Und das bin ich!
Fernanda: Bravo! Colorează steaua!"""

T["13"] = f"""Fernanda: Lecția șase: Essen und Trinken — mâncare și băutură. Iar cine iubește mâncarea cel mai mult? Mikey, desigur!
Eric: Ich habe Hunger! Ich mag Pizza! {P}
Fernanda: Mi-e foame! Îmi place pizza! Iar maestrul Splinter răspunde:
Eric: Guten Appetit! {P}
Fernanda: Poftă bună! Acum cuvintele.
Eric: die Pizza {P} der Apfel {P} die Banane {P} das Brot {P}
Fernanda: pizza, mărul, banana, pâinea.
Eric: der Käse {P} die Milch {P} das Wasser {P} das Eis {P}
Fernanda: brânza, laptele, apa și... înghețata! Când ceva îți place, spui:
Eric: Ich mag Eis. Lecker! {P}
Fernanda: Îmi place înghețata. Delicios! Iar când nu-ți place:
Eric: Ich mag Käse nicht. Igitt! {P}
Fernanda: Nu-mi place brânza. Bleah! Hai să ne jucăm: Eric spune o mâncare, tu spui „Ich mag" sau „Ich mag... nicht".
Eric: Pizza? {P} Apfel? {P} Banane? {P} Milch? {P}
Fernanda: Super! Acum îți e foame, nu-i așa?"""

T["14"] = f"""Fernanda: Exercițiile cu mâncare. Exercițiul unu: Was magst du? Ce-ți place? Sub fiecare mâncare pune o bifă dacă îți place, sau un x dacă nu-ți place. Eric le spune pe rând.
Eric: die Pizza {P} der Apfel {P} die Banane {P} das Brot {P} der Käse {P} die Milch {P} das Wasser {P} das Eis {P}
Fernanda: Exercițiul doi: Mikeys Pizza! Desenează pe pizza lui Mikey:
Eric: drei Tomaten {P} zwei Pilze {P} fünf Oliven {P} und viel Käse! {P}
Fernanda: Trei roșii, două ciuperci, cinci măsline și multă brânză. Apoi colorează pizza!
Fernanda: Exercițiul trei: scrie peste literele gri: Guten Appetit!
Eric: Guten Appetit! {P}
Fernanda: Exercițiul patru: Und du? Scrie ce îți place și ce nu. Spune tare:
Eric: Ich mag... {P} Ich mag... nicht. {P}
Fernanda: Excelent! Colorează steaua!"""

T["15"] = f"""Fernanda: Lecția șapte: Mein Körper — corpul meu. Uită-te la desenul mare cu Chris și arată pe tine fiecare parte, în timp ce repeți.
Eric: der Kopf {P}
Fernanda: capul.
Eric: die Haare {P}
Fernanda: părul.
Eric: das Ohr {P}
Fernanda: urechea.
Eric: das Auge {P}
Fernanda: ochiul.
Eric: die Nase {P}
Fernanda: nasul.
Eric: der Mund {P}
Fernanda: gura.
Eric: der Arm {P} die Hand {P}
Fernanda: brațul și mâna.
Eric: der Bauch {P}
Fernanda: burta.
Eric: das Bein {P} der Fuß {P}
Fernanda: piciorul și laba piciorului. Eric, tu ai nas?
Eric: Ich habe keine Nase! Aber ich habe eine Antenne!
Fernanda: Ha! Și acum un joc: „Fernanda sagt" — Fernanda spune. Faci ce zice Eric DOAR dacă începe cu „Fernanda sagt". Altfel, nu te miști! Gata?
Eric: Fernanda sagt: Zeig mir die Nase! {P}
Eric: Fernanda sagt: Zeig mir den Bauch! {P}
Eric: Zeig mir den Kopf! {P}
Fernanda: Te-ai mișcat? Nu trebuia! Nu a spus „Fernanda sagt"! Hi hi.
Eric: Fernanda sagt: Zeig mir den Fuß! {P}
Eric: Fernanda sagt: Zeig mir das Ohr! {P}
Fernanda: Bravo! Marți joacă-l cu Elena, iar tu dai comenzile!"""

T["16"] = f"""Fernanda: Exercițiile cu corpul. Exercițiul unu: Schreib die Wörter! Scrie cuvintele pe liniile de lângă Eric. Cuvintele sunt sus, în căsuțe.
Eric: der Kopf {P} der Arm {P} die Hand {P} das Bein {P} der Fuß {P} die Antenne {P}
Fernanda: Indiciu: linia de sus, din stânga, arată spre antenă. Iar în dreapta sunt mâna și piciorul. Ia-o încet, câte una.
Fernanda: Exercițiul doi: Zeichne einen Roboter! Desenează un robot inventat de tine. Ascultă ce trebuie să aibă:
Eric: ein Kopf {P} drei Augen {P} vier Arme {P} zwei Beine {P} eine Antenne {P}
Fernanda: Un cap, trei ochi, patru brațe, două picioare și o antenă! Apoi dă-i un nume și scrie-l jos. Eric, cum crezi că îl va chema?
Eric: Vielleicht... Eric zwei?
Fernanda: Hi hi! Alege tu! Colorează steaua!"""

T["17"] = f"""Fernanda: Lecția opt: Wie geht's? Ce mai faci? În fiecare marți, Elena te întreabă:
Eric: Wie geht's, Chris? {P}
Fernanda: Și poți răspunde:
Eric: Super! {P} Gut! {P} Es geht. {P} Nicht so gut. {P}
Fernanda: Super, bine, așa și așa, nu prea bine. Și poți adăuga: danke! Acum sentimentele.
Eric: froh {P}
Fernanda: vesel, ca Mikey.
Eric: traurig {P}
Fernanda: trist.
Eric: wütend {P}
Fernanda: furios, ca Raphael când mormăie.
Eric: Ich habe Angst. {P}
Fernanda: Mi-e frică, ca lui Uno.
Eric: müde {P}
Fernanda: obosit, ca Clara seara.
Eric: überrascht {P}
Fernanda: surprins, ca Pip. Cum spui că ești vesel?
Eric: Ich bin froh! {P}
Fernanda: Și obosit?
Eric: Ich bin müde. {P}
Fernanda: Joc: fă o față tristă și spune „Ich bin traurig". {P} Acum o față furioasă: „Ich bin wütend"! {P} Și acum o față veselă: „Ich bin froh"! {P} Bravo, ești un actor!"""

T["18"] = f"""Fernanda: Exercițiile cu sentimente. Exercițiul unu: Verbinde! Unește fiecare față cu cuvântul. Ascultă-l pe Eric:
Eric: traurig {P} müde {P} froh {P} überrascht {P}
Fernanda: Indiciu: fața cu ochii închiși și cu z z este obosită... müde.
Fernanda: Exercițiul doi: Zeichne das Gesicht! Desenează fața potrivită în fiecare cerc.
Eric: froh {P} wütend {P} Angst {P} müde {P}
Fernanda: O față veselă, una furioasă, una speriată și una obosită.
Fernanda: Exercițiul trei: Mein Dienstag mit Elena. În fiecare marți scrie data și încercuiește fața care arată cum te simți. Apoi răspunde-i Elenei:
Eric: Wie geht's dir heute? {P}
Fernanda: Ce mai faci azi? Poți spune: Super, danke! Colorează steaua!"""

T["19"] = f"""Fernanda: Das große Deutsch-Spiel — marele joc de germană! Ai nevoie de un zar și de doi pioni: unul pentru tine, unul pentru Elena, sau pentru mami ori tati. Pornești de la START, lângă avionul meu, și ajungi la ZIEL, adică la sosire.
Eric: Würfle! Geh vor! Mach die Aufgabe!
Fernanda: Aruncă zarul, mergi înainte, fă sarcina din căsuță. Dacă răspunzi bine: super! Dacă greșești, un pas înapoi. Hai să exersăm câteva căsuțe. Căsuța doi:
Eric: Sag „Hallo!" {P}
Fernanda: Căsuța cinci:
Eric: „Wau wau!" Welches Tier? {P}
Fernanda: Der Hund! Căsuța șase:
Eric: Zeig mir die Nase! {P}
Fernanda: Căsuța unsprezece:
Eric: Wie alt bist du? {P}
Fernanda: Ich bin sieben Jahre alt! Căsuța șaptesprezece:
Eric: Welche Farbe hat Deca? {P}
Fernanda: Blau! Iar la ZIEL, la sfârșit, îți iei rămas-bun:
Eric: Tschüss!
Fernanda: Ești pregătit. Viel Spaß — distracție plăcută!"""

T["20"] = f"""Fernanda: Chris... ai ajuns la ultima pagină! Asta este diploma ta: Urkunde!
Eric: Urkunde! Chris spricht Deutsch!
Fernanda: Chris vorbește germană! Acum știi să saluți, să numeri, culorile, animalele, familia, mâncarea, corpul și sentimentele. Pentru fiecare lecție terminată, colorează o stea. Ascultă-l pe Eric:
Eric: eins — Hallo sagen. zwei — zählen. drei — Farben. vier — Tiere. fünf — Familie. sechs — Essen. sieben — Körper. acht — Gefühle.
Fernanda: Opt stele, opt lecții! Roagă-o pe Elena să semneze diploma, iar tu semnezi lângă ea. Toți prietenii tăi sunt foarte mândri de tine: Pip, Clara, țestoasele, Uno, Deca... și eu, desigur.
Eric: Super, Chris! Du bist toll! Tschüss — bis Dienstag!
Fernanda: Tu ești grozav! Pa, pe marțea viitoare! Tschüss!"""


def get_key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    return k or getpass.getpass("Cheie Gemini API (nu se afișează): ").strip()


def api(url, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def tts_models(key):
    names, tok = [], ""
    while True:
        d = api("https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000" + (f"&pageToken={tok}" if tok else ""), key)
        names += [m["name"].split("/", 1)[1] for m in d.get("models", []) if "tts" in m["name"].lower()]
        tok = d.get("nextPageToken")
        if not tok:
            return names


def pick(models):
    for v in PREFERRED:
        hits = [m for m in models if v in m]
        if hits:
            return sorted(hits, key=lambda m: ("pro" in m, m))[0]
    return None


def tts(key, model, text):
    body = {
        "contents": [{"parts": [{"text": DIRECTOR + text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"multiSpeakerVoiceConfig": {"speakerVoiceConfigs": [
                {"speaker": s, "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v}}} for s, v in VOICES.items()]}},
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for attempt in range(5):
        try:
            part = api(url, key, body)["candidates"][0]["content"]["parts"][0]["inlineData"]
            return base64.b64decode(part["data"]), part.get("mimeType", "")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 4:
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}") from None


def save(pcm, mime, name):
    wav, mp3 = os.path.join(OUT, name + ".wav"), os.path.join(OUT, name + ".mp3")
    if "wav" in mime.lower():
        open(wav, "wb").write(pcm)
    else:
        m = re.search(r"rate=(\d+)", mime)
        with wave.open(wav, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(m.group(1)) if m else 24000)
            w.writeframes(pcm)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", mp3], check=True)
    os.remove(wav)
    return mp3


def main():
    args = sys.argv[1:]
    key = get_key()
    models = tts_models(key)
    if "--list" in args:
        print("\n".join(models)); return
    model = pick(models)
    if not model:
        sys.exit("Niciun model TTS găsit. Disponibile: " + ", ".join(models))
    print(f"Model: {model}   (TTS disponibile: {', '.join(models)})", flush=True)
    os.makedirs(OUT, exist_ok=True)
    todo = [a for a in args if not a.startswith("--")] or list(T)
    for name in todo:
        mp3 = os.path.join(OUT, name + ".mp3")
        if os.path.exists(mp3) and "--force" not in args:
            print(f"skip {name}.mp3 (există)"); continue
        pcm, mime = tts(key, model, T[name])
        save(pcm, mime, name)
        print(f"OK {name}.mp3  {os.path.getsize(mp3) // 1024} KB", flush=True)
    print("GATA")


if __name__ == "__main__":
    main()
