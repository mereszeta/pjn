import fastai
from fastai.text import *
from sentencepiece import SentencePieceProcessor

wgts_path = "./work/up_low50k/models/fwd_v50k_finetune_lm_enc.h5"
model_path = "./work/up_low50k/tmp/sp-50k.model"

processor = SentencePieceProcessor()
processor.Load(model_path)
processor.SetEncodeExtraOptions("bos:eos")
processor.SetDecodeExtraOptions("bos:eos")

bptt = 5
max_seq = 100
n_tok = len(processor)
emb_sz = 400
n_hid = 1150
n_layers = 4
pad_token = 1
bidir = False
qrnn = False

rnn = MultiBatchRNN(bptt, max_seq, n_tok, emb_sz, n_hid, n_layers, pad_token,
                    bidir, qrnn)
model = SequentialRNN(rnn, LinearDecoder(n_tok, emb_sz, 0, tie_encoder=rnn.encoder))

load_model(model[0], wgts_path)
model.reset()
model.eval()


# From infer.py
class LMTextDataset(Dataset):
    def __init__(self, x):
        self.x = x

    def __getitem__(self, idx):
        sentence = self.x[idx]
        return sentence[:-1], sentence[1:]


def next_token(sentence, model):
    ids = [np.array(processor.encode_as_ids(sentence))]
    # From infer.py
    dataset = LMTextDataset(ids)
    sampler = SortSampler(ids, key=lambda x: len(ids[x]))
    dl = DataLoader(dataset,
                    batch_size=100,
                    transpose=True,
                    pad_idx=1,
                    sampler=sampler,
                    pre_pad=False)

    tensors = None
    with no_grad_context():
        for entry in dl:
            tensors = model(entry[0])
    last = tensors[0][-1]

    best_prediction_id = int(torch.argmax(last))
    best_prediction_word = processor.decode_ids([best_prediction_id])

    while best_prediction_id in ids[0] or not is_word(best_prediction_word):
        last[best_prediction_id] = -1
        best_prediction_id = int(torch.argmax(last))
        best_prediction_word = processor.decode_ids([best_prediction_id])

    return best_prediction_word


def is_word(token):
    return token.isalpha() and (len(token) > 1 or is_one_char(token))


def is_one_char(token): return token in ['a', 'i', 'o', 'u', 'w', 'z']


def prediction(sent, mdl):
    wc = 30
    result = ""
    for _ in range(wc):
        result += " " + next_token(sent + " " + result, mdl)
    return result


sentences = [
    "Warszawa to największe",
    "Te zabawki należą do",
    "Policjant przygląda się",
    "Na środku skrzyżowania widać",
    "Właściciel samochodu widział złodzieja z",
    "Prezydent z premierem rozmawiali wczoraj o",
    "Witaj drogi",
]
print("Predictions for short sentences: ")
print("\n")

for sent in sentences:
    print(sent + prediction(sent, model))

questions = [
    "Gdybym wiedział wtedy dokładnie to co wiem teraz, to bym się nie",
    "Gdybym wiedziała wtedy dokładnie to co wiem teraz, to bym się nie"
]

print("Predictions for questions: ")
print("\n")

for question in questions:
    print(question + prediction(question, model))

print("Prediction for long text: ")

long_text = "Polscy naukowcy odkryli w Tatrach nowy gatunek istoty żywej. Zwięrzę to przypomina małpę, lecz porusza się na " \
            "dwóch nogach i potrafi posługiwać się narzędziami. Przy dłuższej obserwacji okazało się, że potrafi również " \
            "posługiwać się językiem polskim, a konkretnie gwarą podhalańską. Zwierzę to zostało nazwane "

print(long_text + prediction(long_text, model))
