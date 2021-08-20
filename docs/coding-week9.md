# Statistics and benchmarking
During the ninth week we have been testing the performance of the application by testing it with 10000 DBpedia abstracts. With this we intend to obtain several metrics such as the number of simple sentences, complex sentences, number of lexicalization failures, etc. In addition, the local DBpedia spotlight server has been installed to use it instead of the online API.

## DBpedia spotlight local installation
The first step was the installation of the DBpedia Spotlight local server. Until now we had been using only the online API, because it was more convenient to use the online API instead of deploying our own server.

The main reason for the decision to change is the difference in response time between the online API and the local server. As expected, the response time of the local server is much lower than the online service. In addition, the Spotlight API limits the number of requests from time to time, so it is not a good alternative for the tests to be done during this week.
On the other hand, it is suspected that the model used in the online API is not the latest version.

The downside of opening the local server is that it occupies 8 Gb in RAM. Luckily I have a 32 Gb machine and it is not a problem, but it is still a large amount of memory.

The folder with the Spotlight server related files and a short guide on how to install it can be found [here][3]. Both the model and the server file are not on Github as they exceed the maximum allowed size, if you want to install it please read the file [Readme.md][4].

## General clean up of the Github repository
This week we have also taken the opportunity to clean up and organize the project structure in Github since we are close to the end of the project. 
 
Now, in all the folders there is a readme file that indicates what each file does inside that folder.
In addition, all the code has been moved to two folders: The scripts folder contains those files that have been used at some point in the execution of the project and that are not part of the main pipeline. The codingweeks folder contains one python file for each week with the formation cw+week number. These files constitute the main pipeline and have been made this way to be able to distinguish well the difference between the previous week and the current week.

In the last week a new folder with the web application will be created.

## Stats
How many simple sentences, complex sentences, rdf triplets, how many times class lookup fails when to be, etc.

To fix: Token indices sequence length is longer than the specified maximum sequence length for this model (620 > 512). Running this sequence through the model will result in indexing errors

```
Run with 10000 abstracts, only simple sentences:

Num of abstracts 9938
Simple sentences: 21817, from each text avg of 2.195310927752063 simple sentences
Complex sentences: 17116, from each text avg of 1.7222781243711007 complex sentences
Total number of sentences 38933
Number of normal text triples 28783, from each text avg of 2.896256792111089 triplets
Number of normal text triples 43231, from each text avg of 4.350070436707587 triplets
4122

[The 2018 Cotton Bowl Classic | was | one of the 2018–19 bowl games concluding the 2018 FBS football season, a public secondary school located in Lavender Hill in the Cape Flats district of Cape Town , Western Cape , South Africa | are | Afrikaans, a public secondary school located in Lavender Hill in the Cape Flats district of Cape Town , Western Cape , South Africa | are | English, Bhomita Talukdar ( Assamese : ভমিতা তালুকদাৰ ) , alias Deepali , | was | the organisational secretary of the women 's wing of ULFA, Bhomita Talukdar ( Assamese : ভমিতা তালুকদাৰ ) , alias Deepali , | is | the wife of Arun Mahanta , a hardcore ULFA militant of Barpeta]
```

## Conclusions
In conclusion, during this week... 

In the next week .

For more information please check the [repository][1] or the [source file of this coding week 9][2].

[1]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/cw9.py
[3]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/tree/main/spotlight
[4]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/spotlight/Readme.md


