from vocab import Vocabulary
from model import EncoderCNN, DecoderRNN 
from configuration import Config
from PIL import Image
from torch.autograd import Variable 
import torch
import torchvision.transforms as T 
import matplotlib.pyplot as plt
import numpy as np 
import argparse
import pickle 
import os


def main(image):
    # Configuration for hyper-parameters
    config = Config()
    
    # Image Preprocessing
    transform = config.test_transform

    # Load vocabulary
    with open(os.path.join(config.vocab_path, 'vocab.pkl'), 'rb') as f:
        vocab = pickle.load(f)

    # Build Models
    encoder = EncoderCNN(config.embed_size)
    encoder.eval()  # evaluation mode (BN uses moving mean/variance)
    decoder = DecoderRNN(config.embed_size, config.hidden_size, 
                         len(vocab), config.num_layers)
    

    # Load the trained model parameters
    encoder.load_state_dict(torch.load(os.path.join(config.teacher_cnn_path, 
                                                    config.trained_encoder)))
    decoder.load_state_dict(torch.load(os.path.join(config.teacher_lstm_path, 
                                                    config.trained_decoder)))
    # Prepare Image       
    image = Image.open(image)
    image_tensor = Variable(transform(image).unsqueeze(0))
    
    # Set initial states
    state = (Variable(torch.zeros(config.num_layers, 1, config.hidden_size)),
             Variable(torch.zeros(config.num_layers, 1, config.hidden_size)))
    
    # If use gpu
    if torch.cuda.is_available():
        encoder.cuda()
        decoder.cuda()
        state = [s.cuda() for s in state]
        image_tensor = image_tensor.cuda()
    
    # Generate caption from image
    feature = encoder(image_tensor)
    sampled_ids = decoder.sample(feature, state)
    sampled_ids = sampled_ids.cpu().data.numpy()
    
    # Decode word_ids to words
    sampled_caption = []
    for word_id in sampled_ids:
        word = vocab.idx2word[word_id]
        sampled_caption.append(word)
	if word_id==96 :
		sampled_caption.append('<end>')
		break
        if word == '<end>':
            break
    sentence = ' '.join(sampled_caption)
    
    # Print out image and generated caption.
    print (sentence)
    return sentence 
if __name__ == '__main__':
    path='../coco/val2017/'
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, required=False, help='image for generating caption')
    args = parser.parse_args()
    print(args)
    params = vars(args)
    if(params['image'] is not None):
        main(params['image'])
    else:
       imagelist=os.listdir(path);
       for i in range(0,5):
           imagepath=path+imagelist[i];
           print(imagepath)
           main(imagepath)
            
    
