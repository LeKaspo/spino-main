import json 
command = {
        "type" : "VkrYDJEc1P4H0ICDqVz6",
        "params" : {
            "param1" : "QeJDIDNwBz59uAhIPAsI",
            "param1" : "L6mhmhFY1ceNaiuBqVNl",
            "param1" : "d4Ztxctt4j0AVzVUOzp6",
            "param1" : "w3KtvqjpCYdmT19KOmYA",
            "param1" : "AYByryMeLVTpR76yW4RV",
        },
        "secondaryparams" : {
            "param1" : "QeaaIDNwBz59uAhIPAsI",
            "param1" : "L6mhaaFY1ceNaiuBqVNl",
            "param1" : "d4Ztxcaa4j0AVzVUOzp6",
            "param1" : "w3KtvqjpaadmT19KOmYA",
            "param1" : "AYByryMeLVTpR76aa4RV",
        }
    }
message = json.dumps(command).encode('utf-8')

print(f"Message which holds: {command}")
print(message)
print("Length of message:")
print(len(message))