import sys, pickle, os, random
import numpy as np
        
def read_corpus(corpus_path):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data
    """
    data = []
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    sent_, tag_ = [], []
    for line in lines:
        if line != '\n':
            char_label = line.strip().split()
            if len(char_label)<2 or len(char_label)>2: continue
            [char, label] = char_label
            sent_.append(char)
            tag_.append(label)
        else:
            data.append((sent_, tag_))
            sent_, tag_ = [], []
    return data


def vocab_build(vocab_path, corpus_path, min_count):
    """

    :param vocab_path:
    :param corpus_path:
    :param min_count:
    :return:
    """
    data = read_corpus(corpus_path)
    word2id = {}
    for sent_, tag_ in data:
        for word in sent_:
            if word.isdigit():
                word = '<NUM>'
            elif ('\u0041' <= word <='\u005a') or ('\u0061' <= word <='\u007a'):
                word = '<ENG>'
            if word not in word2id:
                word2id[word] = [len(word2id)+1, 1]
            else:
                word2id[word][1] += 1
    print(len(word2id))
    low_freq_words = []
    for word, [word_id, word_freq] in word2id.items():
        if word_freq < min_count and word != '<NUM>' and word != '<ENG>':
            low_freq_words.append(word)
    for word in low_freq_words:
        del word2id[word]

    new_id = 1
    for word in word2id.keys():
        word2id[word] = new_id
        new_id += 1
    word2id['<UNK>'] = new_id
    word2id['<PAD>'] = 0

    print(len(word2id))
    with open(vocab_path, 'wb') as fw:
        pickle.dump(word2id, fw)


def sentence2id(sent, word2id):
    """

    :param sent:
    :param word2id:
    :return:
    """
    sentence_id = []
    for word in sent:
        if word.isdigit():
            word = '<NUM>'
        elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
            word = '<ENG>'
        if word not in word2id:
            word = '<UNK>'
        sentence_id.append(word2id[word])
    return sentence_id


def read_dictionary(vocab_path):
    """

    :param vocab_path:
    :return:
    """
    vocab_path = os.path.join(vocab_path)
    with open(vocab_path, 'rb') as fr:
        word2id = pickle.load(fr)
    print('vocab_size:', len(word2id))
    return word2id


def random_embedding(vocab, embedding_dim):
    """
    :param vocab:
    :param embedding_dim:
    :return:
    """
    embedding_mat = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))
    embedding_mat = np.float32(embedding_mat)
    return embedding_mat


def pad_sequences(sequences, pad_mark=0):
    """
    :param sequences:
    :param pad_mark:
    :return:
    """
    max_len = max(map(lambda x : len(x), sequences))
    seq_list, seq_len_list = [], []
    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_len] + [pad_mark] * max(max_len - len(seq), 0)
        seq_list.append(seq_)
        seq_len_list.append(min(len(seq), max_len))
    return seq_list, seq_len_list


def batch_yield(data, batch_size, vocab, tag2label, shuffle=False):
    """

    :param data:
    :param batch_size:
    :param vocab:
    :param tag2label:
    :param shuffle:
    :return:
    """
    data_list = []
    if shuffle:
        random.shuffle(data)

    seqs, labels = [], []
    for (sent_, tag_) in data:
        sent_ = sentence2id(sent_, vocab)
        label_ = [tag2label[tag] for tag in tag_]

        if len(seqs) == batch_size:
            data_list.append([seqs, labels])
            seqs, labels = [], []

        seqs.append(sent_)
        labels.append(label_)

    if len(seqs) != 0:
        data_list.append([seqs, labels])
    return data_list

def load_training_data(corpus_path, word_id_map, tag_label_map, batch_size=100):
    data_list = read_corpus(corpus_path)    
    batches = batch_yield(data_list, batch_size, word_id_map, tag_label_map, shuffle=True)
    print("加载数据完毕,数据量是", len(batches))
    return batches
    
def extract_char_vec_from_pretrained():
    lines = list(open('./data_path/pretrained_char_vec.txt', 'r', encoding='utf8').readlines())
    char_vec_map = {}
    for line in lines:
        char_vec = line.replace("\n", '').split(" ")
        char = char_vec[0]
        vec = char_vec[1:]
        vec = list(map(lambda x: float(x), vec))
        char_vec_map[char] = vec

    char_id = pickle.load(open('./data_path/word2id.pkl', 'rb'))
    char_id = list(char_id.items())
    embending = np.zeros((len(char_id), len(vec)))
    for i in range(len(char_id)):
        [char, id] = char_id[i]
        if char in char_vec:
            embending[i, :] = char_vec_map[char]
    pickle.dump(embending, open('./data_path/pretrained_char_vec.pkl', 'wb'))


if __name__ == '__main__':
    vocab_build('./data_path/word2id.pkl', './data_path/train_data', min_count=5)
    
    
