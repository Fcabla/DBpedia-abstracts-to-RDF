import os

folders = next(os.walk('./'))[1]

for folder in folders:
    with open(f"./{folder}/{folder}_results.txt", encoding="utf-8") as file:
        n_pos = 0
        n_neg = 0
        for line in file:
            if line.find(">>COMPLEX ") > 0:
                if line[:1] == '+':
                    n_pos = n_pos + 1
                else:
                    n_neg = n_neg + 1
    file.close()
    print(f"Results for {folder}:")
    print(n_pos + n_neg, "sentencias analizadas")
    print(f"{n_pos} aciertos ({n_pos/(n_pos + n_neg):.2f}%)")
    print(f"{n_neg} aciertos ({n_neg/(n_pos + n_neg):.2f}%)")
    print("=======================================")
