---
title: "CAM(Class Acitvation Map) Implementation"
excerpt: "Learning Deep Features for Discriminative Localization"
use_math: true
comments: true

last_modified_at: 2020-08-04T03:41
---


Today, I'm going to talk about a paper, 'Learning Deep Features for Discriminative Localization'([Zhou+ CVPR16](https://arxiv.org/pdf/1512.04150.pdf)).
I'll review this paper lightly first and try to implement the main functions of CAM with Pytorch, which are introduced in the paper.  
  
## Background

Over a long history of CNN, people made a great effort to increase the accuracy of the trained model. Since 2012, deep learning techniques have developed overwhelmingly 
and have now surpassed human beings in terms of object recognition.
However, what they had known was that filters could find the edge of an object at the shallow layers and capture the high-dimensional features as the network goes deeper.
The important thing is, they didn't know why the machine made such a judgment when it was asked to guess what the object was. 
That is to say, there was not any method that could explain the process of the machine's thinking.  
  
*CAM*, which was developed by Bolei Zhou+ in 2016, is the very way to solve this problem. 
Using CAM, we can interpret an image from the machine's point of view and explain which parts of the image are utilized to make a decision.

## Introduction

In this paper, the author showed that trained CNN model is successfully able to localize the discriminative regions of an object for classification despite no data on the location
of the object was provided.  

Generally, a CNN model has a Fully-Connected layer(FC) at the last part of the network, which is used to generate the final output. To use the FC layer, however, the features 
need to be flattened while losing the spatial information that convolution layers accumulated through the previous parts of the network.
This is the main reason that makes the model lose the ability to localize objects.  
Recently, popular CNN models such as NIN(Network in Network) and GoogLeNet have been proposed to avoid FC layer not only to keep the localization ability which is mentioned 
above, but also to minimize the number of parameters while maintaining high performance.  
In order to achive this, the author just applied GAP(global average pooling) to the model.
The use of GAP prevented overfitting during training and encouraged the network to identify the complete extent of the object at the same time.
After the application of GAP, trained CNN model actually gets to build a generic localizable deep representation that exposes the implicit attention of CNNs on an image.

What we have to look at is that while GAP is not a novel techinique at all, which is even simple technique with little computational cost, the unique observation that it can be
applied for accurate discriminative localizations offered a new paradigm in ML model analysis.  
This approach should be the core contribution of this paper and it provides us with another glimpse into the soul of CNNs.  

## Class Activation Map(CAM)

CAM actually works at the end of the network, just before the final output layer(softmax layer in the case of categorization).
At this point, GAP is applied to the convolutional feature maps and the features after the GAP layer finally pass through the last FC layer.
(This network uses only one FC layer)
And then, CAM identifies the importance of the image regions by projecting back the weights of the output layer onto the convolutional feature maps. 

**To explain the concept with equations,**  
>Let $f_k(x,y)$ represent the activation of unit $k$ in the last convolutional layer at spatial location $(x,y)$. Then, for unit $k$, the result of performing GAP is expressed
as $F^k$ and it equals to $\sum_{x, y}f_k(x,y)$. Thus for a given class c, the input to the softmax, $S_c$ is $\sum_k w_{k}^{c}F_k$, where $w_{k}^{c}$ is the weight 
corresponding to class $c$ for unit $k$. Essentially, $w_{k}^{c}$ indicates the importnace of $F_k$ for class $c$.  
To sum up, it becomes 
>
$$\begin{matrix}
S_c &=& \sum_k w_k^c F_k \\
&=& \sum_k w_c^k \sum_{x, y}f_k(x,y) \\
&=& \sum_{x, y} \sum_k w_k^c f_k(x,y) 
\end{matrix}$$
>
like this.  
If we define $M_c$ as the CAM for class $c$, where each spatial element is given by $M_c(x, y) = \sum_k w_k^c f_k(x, y)$, we can find $S_c = \sum_{x, y} M_c(x, y)$.  
Hence, $M_c(x,y)$ directly indicates the importance of the activation at spatial grid $(x,y)$ leading to the classification of an image to class c.

Therefore, the class activation map is simply a weighted linear sum of the presence of visual patterns at different spatial location. By simply upsampling the class activation map 
to the size of the input image, the regions of the image that are most relevant to the particular category can be identified.

![structure](https://drive.google.com/uc?export=view&id=1NXXxd6T0XWR455qImxqG3-WX762Q78SG){: .align-center}

## Implementation

I tried to implement the main functions of the original project and visually check their results.
You can refer to the code [here(CAM implementation code)](https://github.com/froggydisk/CAM).
I used Pytorch and you can simply run the code on GoogleColab. 

I made a very simple network first and used CIFAR10 for training.
After the training is finished, the model becomes able to classify an object and we can find the class with the highest probability.
Then, we can draw a heatmap by multiplying the corresponding weights with each feature maps that came out from the last convolutional layer.  

The code below shows the main parts of the CAM function.

```python
feature_collection = [] 
def get_feature(input):                                         # get features from the input
  _, feature = net(input)
  feature_collection.append(feature.cpu().data.numpy())

params = list(net.parameters())
weight_for_softmax = np.squeeze(params[-2].cpu().data.numpy())  # get weights from the final layer

def Do_CAM(feature, weigth_for_softmax, class_id):                   # draw a heatmap
  upsample_size = (img_size, img_size)
  _, c, h, w = feature.shape
  cam = np.dot(weight_for_softmax[class_id],feature.reshape(c, h*w)) # (weights) x (feature maps)  
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

Here is examples.  

![test1](https://drive.google.com/uc?export=view&id=1lHqpu8QE8PMa8BuIzwbiJQNOV_5HZ9xe) ![cam1](https://drive.google.com/uc?export=view&id=1uAmApd8PnsCBixmM6whvkBPmrVF5LGV7)  
![test2](https://drive.google.com/uc?export=view&id=1coE6aIaoZ-lgrqsOnHE9HIuRHj1dImwh) ![cam2](https://drive.google.com/uc?export=view&id=108Y6Ds_sZ7FkruX7qThMdt5RrrPo2VQf)  
![test3](https://drive.google.com/uc?export=view&id=1hOUnEG8qpj8-GafGajwie7PAUI6nyGbh) ![cam3](https://drive.google.com/uc?export=view&id=1V84PrTRS3EALuSb2_3stXYas-Den0alc)  

It would be a bit hard to see the results because the size of CIFAR10 images is 32x32.  
I would recommend you to train the model with another dataset if possible, or just take a pretrained model like GoogLeNet for better results.
If you use the pretrained model, you don't need to train it anymore. You can use it as it is.

And this is the comparison between 5-epoch-experiment and 50-epoch-experiment.

5 Epoch &nbsp;&nbsp;&nbsp;&nbsp; 50 Epoch  
![epoch5-1](https://drive.google.com/uc?export=view&id=1RzaGt4mPik8XDlg5JNsX7hkHlVYQ3YoJ "5 epochs") ![epoch50-1](https://drive.google.com/uc?export=view&id=1qsuT5nWGhiWcWD_nm_z4AF72WI-JHj0z "50 epochs")  
![epoch5-2](https://drive.google.com/uc?export=view&id=16EGjSSm3yOuTQFkG_F0zhI0pVhMkUbd_ "5 epochs") ![epoch50-2](https://drive.google.com/uc?export=view&id=1XM2-WKZXxxkBtmi9_QqRkre0W4-ujKOe "50 epochs")

You can find the model concentrates on the details of the image as the number of epochs increases.

## Reference

[https://kangbk0120.github.io/articles/2018-02/cam](https://kangbk0120.github.io/articles/2018-02/cam)