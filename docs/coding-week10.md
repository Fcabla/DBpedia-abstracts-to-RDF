# Web application demo
In the last week I have dedicated myself mainly to the creation of a web application to demonstrate the operation of the pipeline developed during the last 9 weeks. In addition, it is intended to create an alternative that works via command line.

## Web framework
The first step in the creation of a web application is to choose which tool or framework best suits our development. Based on the python language there are many frameworks such as flask, django, pyramid or bottle among others.

Initially we had the idea of building the application using [Flask][3] as it is a very simple and lightweight framework. After several days testing this tool and trying to build the web application i was struggling with some parts of this framework, mainly with the frontend part since i have not a lot of experience with html+css (bootstrap).

Looking for alternatives I found another tool to generate web pages very similar to Shiny (from R). It is [streamlit][4], an open-source framework that is intended to build web applications for Machine Learning and Data Science. This framework allows you to write an app the same way you write a python code, making it seamless to work on the interactive loop of coding and viewing results in the web app.

To install this tool just run the following command: `pip3 install streamlit`.

## Web App
The basic operation of the web application is that the user enters a text as input and a ttl file is generated with the generated RDF triples. Apart from this main function we have included some interactive elements so that the user can customize how the triples are processed or what kind of outputs will be shown on the screen.

Using the default streamlit theme we have managed to build the following user interface:

![webapp_main_view](https://raw.githubusercontent.com/Fcabla/DBpedia-abstracts-to-RDF/main/docs/webapp_main_view.png)

Como se puede observar en la imagen 
![webapp_output1](https://raw.githubusercontent.com/Fcabla/DBpedia-abstracts-to-RDF/main/docs/webapp_output1.png)

![webapp_output2](https://raw.githubusercontent.com/Fcabla/DBpedia-abstracts-to-RDF/main/docs/webapp_output2.png)

## Final evaluation period
Being this the last week, I have dedicated some time to generate documentation, test the application, prepare the github repository and evaluate both my mentor and DBpedia. During this evaluation I also had to give my opinion about certain aspects of Google Summer of Code as well as explain what I found the most difficult and the most enjoyable aspects of this journey.

## Conclusions
In conclusion, during this week we have been able to build a web applications to allow the users to test the pipeline.


For more information please check the [repository][1] or the [folder containing the web app][2].

[1]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/codingweeks/webapp
[3]: https://flask.palletsprojects.com/en/2.0.x/
[4]: https://streamlit.io/
