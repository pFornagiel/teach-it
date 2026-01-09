from vectorstore import build_vectorstore
from tutor import build_tutor

files = [
    "hackathon_source_materials/lecture_1/korylator_lumiczny.txt"
]

vectorstore = build_vectorstore(files)
tutor = build_tutor(vectorstore)

while True:
    q = input("\nZadaj pytanie (exit aby zakończyć): ")
    if q.lower() == "exit":
        break

    result = tutor(q)
    print("\nODPOWIEDŹ:\n", result["result"])
