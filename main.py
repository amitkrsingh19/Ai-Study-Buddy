import json
from graph.pipeline import graph

initial_state = {"topic":"Machine learning","level":"Advanced"}

if __name__=="__main__":
  response = graph.invoke(initial_state) # type:ignore
  print(response)

  with open("day-9.json", 'w', encoding = 'utf-8') as f:
    json.dump(response, f , indent=4)
    print("Saved response as json")