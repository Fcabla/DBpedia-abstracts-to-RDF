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

Como se puede observar en la imagen, el principal componente gráfico es el área de texto donde el usuario introduce un texto (por ejemplo un abstract de una página de DBpedia). Además, existen cuatro casillas de verificación:
1. Utilizar todas las frases: Si es verdadera se utilizarán todas las frases para generar las triplas (no sólo las frases simples), se aconseja a los usuarios que dejen esta opción sin marcar ya que la calidad de las triplas de las frases complejas es peor que la de las triples de las simples.

2. Mostrar las frases simplificadas: Si es verdadero los triples de texto se imprimirán en la página web como una salida extra.

3. Obtener sólo las triplas sin literales: Si es true sólo se seleccionarán las triplas que no tengan errores en la estructura, aquellas triplas que sigan el patrón recurso | propiedad | recurso.

4. Imprimir información de depuración: Si es true se imprimirá al final de la página web cada sentencia con las triplas generadas a partir de ella.

En las siguientes dos imágenes se muestra el output de las tripletas RDF, las tripletas de texto (sentencias simplificadas) y la información de debug:

![webapp_output1](https://raw.githubusercontent.com/Fcabla/DBpedia-abstracts-to-RDF/main/docs/webapp_output1.png)

![webapp_output2](https://raw.githubusercontent.com/Fcabla/DBpedia-abstracts-to-RDF/main/docs/webapp_output2.png)

Una vez que un usuario hace click en el botón **submit** se genera al principio de los outputs un enlace para descargar el archivo ttl generado. Aunque he insistido con que esta herramienta facilita mucho la construcción de páginas web, he encotrado muchas dificultades a la hora de generar una forma de descargar el fichero.
Por defecto streamlit no incluye ninguna función para que los usuarios descarguen archivos, por lo que se ha tenido que hacer manualmente. Para más información sobre este problema consulte la siguiente [función][5]

## Final evaluation period
Being this the last week, I have dedicated some time to generate documentation, test the application, prepare the github repository and evaluate both my mentor and DBpedia. During this evaluation I also had to give my opinion about certain aspects of Google Summer of Code as well as explain what I found the most difficult and the most enjoyable aspects of this journey.

## Conclusions
In conclusion, during this week i have been able to build a web applications to allow the users to test the pipeline. In addition, I have generated more documentation, cleaned up the repository and performed the final evaluation.

This has been an amazing journey in which I have had the opportunity to learn many concepts in the area of natural language processing as well as gaining a lot of experience with the Python programming language. Also, this has been the first time that I have participated in an Open Source project and I really enjoyed the experience, I will certainly continue contributing to this kind of projects.

Finally I would like to thank both my tutor and the DBpedia organization for their help and for the opportunity to participate with them in this interesting project that has undoubtedly contributed to my personal enrichment.

Note: Although the project is formally finished (according to the schedule established by GSoc), I intend to tweak, add or improve some small details during this week.

For more information please check the [repository][1] or the [folder containing the web app][2].

[1]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/codingweeks/webapp
[3]: https://flask.palletsprojects.com/en/2.0.x/
[4]: https://streamlit.io/
[5]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/c8ac79a5b26f0d11ae326b034260140bd958a0f8/code/webapp/app.py#L66