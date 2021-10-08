import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm
import os

# converter strings para  integer


def atoi(s):
    n = 0
    for i in s:
        n = n*10 + ord(i) - ord("0")
    return n


# Criar  as respectivas pastas teste e treino que irá conter as pastas com as imagens especificas
outer_names = ['test', 'train']
inner_names = ['angry', 'disgusted', 'fearful',
               'happy', 'sad', 'surprised', 'neutral']
os.makedirs('data', exist_ok=True)
for outer_name in outer_names:
    os.makedirs(os.path.join('data', outer_name), exist_ok=True)
    for inner_name in inner_names:
        os.makedirs(os.path.join('data', outer_name,
                                 inner_name), exist_ok=True)

# Manter a conta de cada categoria
angry = 0
disgusted = 0
fearful = 0
happy = 0
sad = 0
surprised = 0
neutral = 0
angry_test = 0
disgusted_test = 0
fearful_test = 0
happy_test = 0
sad_test = 0
surprised_test = 0
neutral_test = 0

df = pd.read_csv('fer2013.csv')
mat = np.zeros((48, 48), dtype=np.uint8)
print("Guardando imagens...")


for i in tqdm(range(len(df))):
    txt = df['pixels'][i]
    words = txt.split()

    for j in range(2304):
        xind = j // 48
        yind = j % 48
        mat[xind][yind] = atoi(words[j])

    img = Image.fromarray(mat)

    if i < 28709:
        if df['emotion'][i] == 0:
            img.save('treino/zangado/im'+str(angry)+'.png')
            angry += 1
        elif df['emotion'][i] == 1:
            img.save('treino/desgosto/im'+str(disgusted)+'.png')
            disgusted += 1
        elif df['emotion'][i] == 2:
            img.save('treino/medo/im'+str(fearful)+'.png')
            fearful += 1
        elif df['emotion'][i] == 3:
            img.save('treino/feliz/im'+str(happy)+'.png')
            happy += 1
        elif df['emotion'][i] == 4:
            img.save('treino/triste/im'+str(sad)+'.png')
            sad += 1
        elif df['emotion'][i] == 5:
            img.save('treino/surpresa/im'+str(surprised)+'.png')
            surprised += 1
        elif df['emotion'][i] == 6:
            img.save('treino/neutro/im'+str(neutral)+'.png')
            neutral += 1

    # test
    else:
        if df['emotion'][i] == 0:
            img.save('teste/zangado/im'+str(angry_test)+'.png')
            angry_test += 1
        elif df['emotion'][i] == 1:
            img.save('teste/desgosto/im'+str(disgusted_test)+'.png')
            disgusted_test += 1
        elif df['emotion'][i] == 2:
            img.save('teste/medo/im'+str(fearful_test)+'.png')
            fearful_test += 1
        elif df['emotion'][i] == 3:
            img.save('teste/feliz/im'+str(happy_test)+'.png')
            happy_test += 1
        elif df['emotion'][i] == 4:
            img.save('teste/triste/im'+str(sad_test)+'.png')
            sad_test += 1
        elif df['emotion'][i] == 5:
            img.save('teste/surpresa/im'+str(surprised_test)+'.png')
            surprised_test += 1
        elif df['emotion'][i] == 6:
            img.save('teste/neutro/im'+str(neutral_test)+'.png')
            neutral_test += 1

print("Dataset Criado")
