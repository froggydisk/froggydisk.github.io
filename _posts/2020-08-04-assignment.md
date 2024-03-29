---
title: "CAM: Class Activation Map Implementation"
excerpt: "Learning Deep Features for Discriminative Localization"
use_math: true
comments: true

categories:
  - Assignment
tags:
  - Pytorch

last_modified_at: 2020-08-04T03:41
---

<br>
<p align="justify">
Today, I'm going to talk about a paper, 'Learning Deep Features for Discriminative Localization'
(<a href="https://arxiv.org/pdf/1512.04150.pdf">Zhou+ CVPR16</a>).
I will review this paper lightly first and try to implement the main functions of CAM with Pytorch, which are introduced in the paper.  
</p>
  
## Background

<p align="justify">
Over a long history of CNN, people made a great effort to increase the accuracy of the trained model. Since 2012, deep learning techniques have developed overwhelmingly 
and have now surpassed human beings in terms of object recognition.
However, what they had known was that filters could find the edge of an object at the shallow layers and capture the high-dimensional features as the network goes deeper.
The important thing is, they didn't know why the machine made such a judgment when it was asked to guess what the object was. 
That is to say, there was not any method that could explain the process of the machine's thinking.  
<br><br>
<em>CAM</em>, which was developed by Bolei Zhou+ in 2016, is the very way to solve this problem. 
Using CAM, we can interpret an image from the machine's point of view and explain which parts of the image are utilized to make a decision.
</p>

## Introduction

<p align="justify">
In this paper, the author showed that trained CNN model is successfully able to localize the discriminative regions of an object for classification despite no data on the location
of the object was provided.  
</p>

<p align="justify">
Generally, a CNN model has a Fully-Connected layer(FC) at the last part of the network, which is used to generate the final output. To use the FC layer, however, the features 
need to be flattened while losing the spatial information that convolution layers accumulated through the previous parts of the network.
This is the main reason that makes the model lose the ability to localize objects.  <br>
Recently, popular CNN models such as NIN(Network in Network) and GoogLeNet have been proposed to avoid FC layer not only to keep the localization ability which is mentioned 
above, but also to minimize the number of parameters while maintaining high performance.  <br>
In order to achive this, the author just applied GAP(global average pooling) to the model.
The use of GAP prevented overfitting during training and encouraged the network to identify the complete extent of the object at the same time.
After the application of GAP, trained CNN model actually gets to build a generic localizable deep representation that exposes the implicit attention of CNNs on an image.
</p>

<p align="justify">
What we have to look at is that while GAP is not a novel techinique at all, which is even simple technique with little computational cost, the unique observation that it can be
applied for accurate discriminative localizations offered a new paradigm in ML model analysis.  <br>
This approach should be the core contribution of this paper and it provides us with another glimpse into the soul of CNNs.  
</p>

## Class Activation Map(CAM)

<p align="justify">
CAM actually works at the end of the network, just before the final output layer(softmax in the case of categorization).
At this point, GAP is applied to the convolutional feature maps and the features after the GAP layer finally pass through the last FC layer.
(This network uses only one FC layer)
And then, CAM identifies the importance of the image regions by projecting back the weights of the output layer onto the convolutional feature maps. 
</p>

**To explain the concept with equations,**  
Let $f_k(x,y)$ represent the activation of unit k in the last convolutional layer at spatial location (x,y). Then, for unit k, the result of performing GAP is expressed
as $F^k$ and it equals to $\sum_{x, y}f_k(x,y)$. Thus for a given class c, the input to the softmax, $S_c$ is $\sum_k w_{k}^{c}F_k$, where $w_{k}^{c}$ is the weight 
corresponding to class c for unit k. Essentially, $w_{k}^{c}$ indicates the importnace of $F_k$ for class c. To sum up, it becomes like this.  

$\begin{matrix}
S_c &=& \sum_k w_k^c F_k \\
&=& \sum_k w_c^k \sum_{x, y}f_k(x,y) \\
&=& \sum_{x, y} \sum_k w_k^c f_k(x,y) 
\end{matrix}$

If we define $M_c$ as the CAM for class c, where each spatial element is given by $M_c(x, y)$ = $\sum_k w_k^c f_k(x, y)$, we can find $S_c = \sum_{x, y} M_c(x, y)$.
Hence, $M_c(x,y)$ directly indicates the importance of the activation at spatial grid (x,y) leading to the classification of an image to class c.

<p align="justify">
Therefore, the class activation map is simply a weighted linear sum of the presence of visual patterns at different spatial location. By simply upsampling the class activation map 
to the size of the input image, the regions of the image that are most relevant to the particular category can be identified.
</p>

![structure](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/CAM%20structure.png?raw=true){: .align-center}

## Implementation

<p align="justify">
I tried to implement the main functions of the original project and visually check their results.
You can refer to the code <a href="https://github.com/froggydisk/CAM">here(CAM Implementation)</a>.
I used Pytorch and you can simply run the code on GoogleColab. 
</p>

<p align="justify">
I made a very simple network first and used CIFAR10 for training.
After the training is finished, the model becomes able to classify an object and we can find the class with the highest probability.
Then, we can draw a heatmap by multiplying the corresponding weights with each feature maps that came out from the last convolutional layer.  
</p>

The code below shows the main parts of the CAM function.

```python
feature_collection = [] 
# get features from the input
def get_feature(input):                                         
  _, feature = net(input)
  feature_collection.append(feature.cpu().data.numpy())

params = list(net.parameters())
# get weights from the final layer
weight_for_softmax = np.squeeze(params[-2].cpu().data.numpy())

# draw a heatmap
def Do_CAM(feature, weigth_for_softmax, class_id): 
  upsample_size = (img_size, img_size)
  _, c, h, w = feature.shape
  # (weights) x (feature maps)
  cam = np.dot(weight_for_softmax[class_id],feature.reshape(c, h*w))  
  cam = cam.reshape(h, w)
  cam = (cam - np.min(cam)) 
  cam = cam / np.max(cam)
  cam = np.uint8(255 * cam)
  cam = cv2.resize(cam, upsample_size)
  return cam
```
By implementing this code, you can get a heatmap of the image you want to see. 

**Settings**
```python
dataset = 'CIFAR10'
img_size = 32
batch_size = 128
epoch = 5
learning_rate = 0.001
```
These are the settings for my experiment. The number of epochs can vary depending on the condition.

Here are some results.  

![test1](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/bird1.jpg?raw=true) ![cam1](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/bird5.png?raw=true)  
![test2](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/horse1.jpg?raw=true) ![cam2](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/horse5-1.png?raw=true)  
![test3](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/ship1.jpeg?raw=true) ![cam3](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/ship40.png?raw=true)  

The results show that class activation maps are highlighting the discriminative object parts detected by the CNN.

While implementing, it would be a bit hard to see the results because the size of CIFAR10 images is 32x32.  
I would recommend you to train the model with another dataset if possible, or just take a pretrained model like GoogLeNet for better results.
If you use the pretrained model, you don't need to train it anymore. You can use it as it is.

And this is the results of comparison between 5-epoch-experiment and 50-epoch-experiment.
I captured the model every 10 epochs during training and observed how the results change. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 5 Epoch 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
50 Epoch  
![epoch5-1](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/dog5-1.png?raw=true "5 epochs") ![epoch50-1](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/dog50-1.png?raw=true "50 epochs")  
![epoch5-2](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/dog5-2.png?raw=true "5 epochs") ![epoch50-2](https://github.com/froggydisk/froggydisk.github.io/blob/master/assets/img/dog50-2.png?raw=true "50 epochs")

As expected, you can find the model concentrates on the details of the image as the number of epochs increases.
Consequently, we can say global average pooling CNNs can perform accurate object localization.

## Reference

[https://kangbk0120.github.io/articles/2018-02/cam](https://kangbk0120.github.io/articles/2018-02/cam)
