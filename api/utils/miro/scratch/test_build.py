from utils.miro.builder import MiroSchemaBuilder
import json
# from stop.models import Stop

# all_stops = Stop.objects.all()

miro_schema = MiroSchemaBuilder('San Pedro de los Pinos')

data = miro_schema.run(reset_bd=True)

data_json = json.dumps(data, indent=2)
connectors_json = json.dumps(miro_schema._connectors, indent=2)

print("skipped\n", data.get('skipped'))
