from preprocessing import clean_text


examples = [
    "Refund not received!!!",
    "Laptop Screen BROKEN.",
    "   Payment     Failed   ",
    "Where is my Order???"
]

for text in examples:
    print("Original :", text)
    print("Cleaned  :", clean_text(text))
    print("-" * 40)