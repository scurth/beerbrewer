import paho.mqtt.client as mqtt
import sys
import getopt
import json
import time

superhelp="""Vorlösen
Diese Raststufe folgt unmittelbar auf das Einmaischen und ermöglicht es den Malzenzymen besonders gut in Lösung zu gehen. Allerdings sind heutige Malze so hochwertig vorverarbeitet, daß dieser Schritt normalerweise nicht mehr notwendig ist.

Temperaturbereich: 18 – 30 °C
Typische Temperatur: 20 °C
Dauer: 20 min. – 12 Std.

Glukanaserast ("Gummirast")
Vor allem Roggen enthält einen hohen Anteil an Glukanen, die ein Bestandteil der Zellwand sind. Sie machen die Würze zähflüssig ("gummiartig"), sodaß ein mit Roggen gebrautes Bier beim Läutervorgang und, je nach Anteil, in der Gärung und sogar beim Trinken unerwünscht klebrig sein kann. Der Abbau durch eine Glukanaserast empfiehlt sich speziell bei Roggenbier.

Temperaturbereich: 35 – 40 °C
Typische Temperatur: 39 °C
Dauer: 15 – 30 min.

Weizenrasten ("Ferularasten")
Besonders Weizenmalz enthält einige Vorläuferstoffe der Ferulasäure, deren Abbauprodukte später zu einigen typischen Weizenbieraromen (wie etwa Nelken) führen. Diese Vorläufer werden zunächst gelöst (Rast 1) und dann zur Ferulasäure abgebaut (Rast 2). Die Rastbereiche liegen eng beieinander.

Temperaturbereiche: 45 und 48 °C
Dauer: je ca. 15 min.

Proteaserast (Eiweißrast)
Jedes Braugetreide enthält Proteine in irgendeiner Form. Einige davon sind erwünscht, etwa Aminosäuren, die der Gärung zugutekommen oder jene Moleküle, die für eine appetitliche Schaumbildung auf dem fertigen Bier sorgen. Andere sind hingegen unerwünscht, da sie zu Kältetrübungen führen

Die meisten heute angebotenen Gerstenmalze sind auch hinsichtlich der Proteine bereits durch das Mälzen gut vorgelöst, sodaß heute oft empfohlen wird, keine Eiweißrast mehr durchzuführen. Da hierzu unterschiedliche Meinungen bestehen und das sicher auch von Malz zu Malz, ja von Charge zu Charge verschieden sein kann, ist diese Entscheidung immer versuchsabhängig. Pauschal läßt sich sagen, daß Weizenmalze generell deutlich mehr (auch ungelöste) Eiweiße enthalten und eine Eiweißrast hier deshalb eher empfehlenswert ist.

Temperaturbereich: 50 – 58 °C
Optimale Temperatur: 52 °C
Dauer: 10 – 20 min.

Maltoserast
Diese mit der nachfolgenden zusammen wichtigste Rast läßt die Stärke des Malzes von den Beta-Amylasen zu vergärbaren Zuckern (Maltose) abbauen und bestimmt damit den späteren Alkoholgehalt des Bieres. Ein konstantes Rühren ist für eine gute Enzymarbeit in dieser Rast unentbehrlich, sodaß viele Hobbybrauer sich hier eines Rührwerks oder eines extra abgestellten Brauhelfers bedienen (im Rahmen der familiären Freizeitgestaltung auch hervorragend für Kinder geeignet).

War die Maische bis zu dieser Rast eher milchig-trüb, läßt sich jetzt der fortschreitende Stärkeabbau verfolgen. Mit fortschreitender Rastdauer wird die Maische klarer und durch den sich zunehmend lösenden Malzzucker auch süßer und klebriger.

Temperaturbereich: 60 – 68 °C
Optimale Temperatur: 63 °C
Dauer: 30 – 90 min.

Verzuckerung
Der Name läßt es ahnen: Hier entstehen in großer Menge aus den langen Stärkemolekülen kürzere Zuckermoleküle. Überwiegend sind das in dieser Rast nicht vergärbare Zucker, die dem späteren Bier Vollmundigkeit und Geschmack geben. Neben der Maltoserast die wichtigste; ein Bier, das ausschließlich aus vergärbaren Zuckern hergestellt würde, ginge ordentlich ins Blut – schmeckte aber nach nichts. (Es soll Flüssigkeiten geben, die diesem Szenario recht nahe kommen.)

Spätestens nach dieser Rast muß der Stärkenachweis durch eine Jodprobe negativ, also jodnormal ausfallen. Sobald dies der Fall ist, kann die Verzuckerung beendet werden.

Temperaturbereich: 68 – 76 °C
Optimale Temperatur: 72 °C
Dauer: 15 – 30 min. (oder bis zur Jodnormalität)

Abmaischen
Wie schon erwähnt, stehen die beiden wärmsten Raststufen in einer Wechselwirkung; was in der heißeren an unvergärbaren Zuckern entsteht, können die Enzyme der kühleren Stufe nachträglich weiter zu vergärbaren Zuckern abbauen. Nicht immer ist dies aber erwünscht. Um ein möglichst vollmundiges Bier mit geringem Alkoholgehalt zu erhalten, muß also die Tätigkeit der Beta-Amylasen nachhaltig beendet werden. Dies geschieht durch Hitze, die übrigens auch dafür sorgt, daß der nachfolgende Läutervorgang durch geringere Viskosität besser abläuft und sich enststandene Zucker mit dem Nachgußwasser besser auswaschen lassen.

Wichtig ist, die Maische auf nicht mehr als 80 °C zu erhitzen, da sich oberhalb dieser Grenze unverzuckerte Stärke und unerwünschte Stoffe aus den Spelzen lösen können, die den Gärverlauf und den späteren Geschmack beeinträchtigen.

Temperaturbereich: 77 – 80 °C
Optimale Temperatur: 78 °C
Dauer: mindestens 20 min. 

Quelle: http://www.besser-bier-brauen.de/selber-bier-brauen/brauanleitungen/detailwissen/maischen/index.html#rasten
"""

starttime=int(time.time())

def usage():
    print("Usage: brew.py [-v] [-V TEMP:MINUTES]")
    print("-v: verbose output, default False")
    print("-V: Vorlösen, default: ", rastphasen_default_json["vorloesen"]["rastzeit"]," Minuten @ ", rastphasen_default_json["vorloesen"]["temperatur"], "°C" )
    print("-G: Glukanaserast, default 39:30 = 39C@30min")
    print("-F1: Ferularasten1, default 45:15 = 45C@15min")
    print("-F2: Ferularasten2, default 48:15 = 48C@15min")
    print("-E: Eiweißrast, default 52:20 = 52C@20min")
    print("-M: Maltoserast, default 63:60 = 63C@60min")
    print("-Z: Verzuckerung, default 72:30 = 72C@30min")
    print("-A: Abmaischen, default 78:20 = 78C@20min")
    print("-p: MQTT Broker Port, default 1883")
    print("-h: show this help")
    print("-s: super help")
    print("-t: mqtt topic")
    pass

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("tinkerforge/callback/ptc_v2_bricklet/NeR/temperature")  

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg

    json_obj=json.loads(msg.payload)
    if "temperature" not in json_obj:
        print("No temperature, skipping")
    else:
        tempcheck(json_obj["temperature"]/100,20)

def tempcheck(current_temperature, target_temperature):
    print("Aktuelle Temperatur: ", current_temperature, " vs Ziel Temperatur: ", target_temperature)
    low_target=target_temperature-1
    if current_temperature < low_target:
        tasmota("on")
    else:
        tasmota("off")

def tasmota(state):
    print("switch to state: ",state)
    print("topic: ", topic)
    ret = client.publish(topic,state)

def on_publish(client,userdata,result):             #create function for callback
    if (verbose is True):
        print("data published \n", result)
        print(ret)
    pass

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        options, prog_argv = getopt.getopt(argv[1:], "hsvV:G:F1:F2:E:M:Z:A:t:p")
    except getopt.GetoptError:
        sys.exit(1)

    global rastphasen_default_json
    rastphasen_default = """
    {
	"vorloesen": {
		"temperatur": 20,
		"rastzeit": 720
	},
	"glukanaserast": {
		"temperatur": 39,
		"rastzeit": 30
	}
    }"""
    rastphasen_default_json = json.loads(rastphasen_default)
    global rastphasen_json
    rastphasen_json = rastphasen_default_json

    for name, value in options:
        if name == "-v":
            global verbose
            verbose = True
        elif name in ("-h"):
            usage()
            sys.exit()
        elif name in ("-s"):
            print(superhelp)
            sys.exit()
        elif name in ("-t"):
            global topic
            topic = value
        elif name in ("-V"):
            print("Value: ", value)
            newvalue=value.split(":")
            rastphasen_json["vorloesen"]["temperatur"]=newvalue[0]
            rastphasen_json["vorloesen"]["rastzeit"]=newvalue[1]


    print(rastphasen_json)
#    print ("Aktuelle Rast Phase:", rastphase)

    global client
    client = mqtt.Client("digi_mqtt_test")  # Create instance of client with client ID “digi_mqtt_test”
    client.on_connect = on_connect  # Define callback function for successful connection
    client.on_message = on_message  # Define callback function for receipt of a message
    client.connect('127.0.0.1', 1883)
    client.loop_forever()  # Start networking daemon
    client.on_publish = on_publish


if __name__ == "__main__":
    main()

