Annotation Processing Tool 详解
------

关于APT（Annotation Processing Tool 简称）的讲解资料很少，幸运地找到了一篇英文的讲解，觉得挺详细的，就翻译过来。[原文](http://hannesdorfmann.com/annotation-processing/annotationprocessing101/) 顺便添加了一些自己的理解，及扩展。

---------------------------------------------------------------------------------------------------------------
在这篇文章中我将阐述如何实现一个注解处理器。首先我将向你解释什么是注解处理器，你可以使用这个强大的工具来做什么及不能做什么。接下来我们将一步一步来实现一个简单的注解处理器。

### 1. 一些基本概念
在开始之前，我们需要声明一件重要的事情是：我们不是在讨论在**运行时**通过反射机制运行处理的注解，而是在讨论在**编译时**处理的注解。
注解处理器是 javac 自带的一个工具，用来在编译时期扫描处理注解信息。你可以为某些注解注册自己的注解处理器。这里，我假设你已经了解什么是注解及如何自定义注解。如果你还未了解注解的话，可以查看[官方文档](http://docs.oracle.com/javase/tutorial/java/annotations/index.html)。注解处理器在 Java 5 的时候就已经存在了，但直到 Java 6 （发布于2006看十二月）的时候才有可用的API。过了一段时间java的使用者们才意识到注解处理器的强大。所以最近几年它才开始流行。
一个特定注解的处理器以 java 源代码（或者已编译的字节码）作为输入，然后生成一些文件（通常是`.java`文件）作为输出。那意味着什么呢？你可以生成 java 代码！这些 java 代码在生成的`.java`文件中。因此你不能改变已经存在的java类，例如添加一个方法。这些生成的 java 文件跟其他手动编写的 java 源代码一样，将会被 javac 编译。

### 2. AbstractProcessor
让我们来看一下处理器的 API。所有的处理器都继承了`AbstractProcessor`，如下所示：
```java
package com.example;

import java.util.LinkedHashSet;
import java.util.Set;
import javax.annotation.processing.AbstractProcessor;
import javax.annotation.processing.ProcessingEnvironment;
import javax.annotation.processing.RoundEnvironment;
import javax.annotation.processing.SupportedAnnotationTypes;
import javax.annotation.processing.SupportedSourceVersion;
import javax.lang.model.SourceVersion;
import javax.lang.model.element.TypeElement;

public class MyProcessor extends AbstractProcessor {

	@Override
	public boolean process(Set<? extends TypeElement> annoations,
			RoundEnvironment env) {
		return false;
	}

	@Override
	public Set<String> getSupportedAnnotationTypes() {
		Set<String> annotataions = new LinkedHashSet<String>();
	    annotataions.add("com.example.MyAnnotation");
	    return annotataions;
	}

	@Override
	public SourceVersion getSupportedSourceVersion() {
		return SourceVersion.latestSupported();
	}

	@Override
	public synchronized void init(ProcessingEnvironment processingEnv) {
		super.init(processingEnv);
	}

}
```

- `init(ProcessingEnvironment processingEnv)` ：所有的注解处理器类**都必须有一个无参构造函数**。然而，有一个特殊的方法`init()`，它会被注解处理工具调用，以`ProcessingEnvironment`作为参数。ProcessingEnvironment 提供了一些实用的工具类`Elements`, `Types`和`Filer`。我们在后面将会使用到它们。

- `process(Set<? extends TypeElement> annoations, RoundEnvironment env)` ：这类似于每个处理器的`main()`方法。你可以在这个方法里面编码实现扫描，处理注解，生成 java 文件。使用`RoundEnvironment` 参数，你可以查询被特定注解标注的元素（原文：you can query for elements annotated with a certain annotation ）。后面我们将会看到详细内容。

- `getSupportedAnnotationTypes()`：在这个方法里面你必须指定哪些注解应该被注解处理器注册。注意，它的返回值是一个`String`集合，包含了你的注解处理器想要处理的注解类型的全称。换句话说，你在这里定义你的注解处理器要处理哪些注解。

- `getSupportedSourceVersion()` ： 用来指定你使用的 java 版本。通常你应该返回`SourceVersion.latestSupported()` 。不过，如果你有足够的理由坚持用 java 6 的话，你也可以返回`SourceVersion.RELEASE_6`。我建议使用`SourceVersion.latestSupported()`。在 Java 7 中，你也可以使用注解的方式来替代重写`getSupportedAnnotationTypes()` 和 `getSupportedSourceVersion()`，如下所示：
```java
@SupportedSourceVersion(value=SourceVersion.RELEASE_7)
@SupportedAnnotationTypes({
   // Set of full qullified annotation type names
	"com.example.MyAnnotation",
	"com.example.AnotherAnnotation"
 })
public class MyProcessor extends AbstractProcessor {

	@Override
	public boolean process(Set<? extends TypeElement> annoations,
			RoundEnvironment env) {
		return false;
	}
	@Override
	public synchronized void init(ProcessingEnvironment processingEnv) {
		super.init(processingEnv);
	}
}
```
由于兼容性问题，特别是对于 android ，我建议重写`getSupportedAnnotationTypes()` 和 `getSupportedSourceVersion()` ，而不是使用 `@SupportedAnnotationTypes` 和 `@SupportedSourceVersion`。

接下来你必须知道的事情是：注解处理器运行在它自己的 JVM 中。是的，你没看错。javac 启动了一个完整的 java 虚拟机来运行注解处理器。这意味着什么？你可以使用任何你在普通 java 程序中使用的东西。使用 `guava`! 你可以使用依赖注入工具，比如`dagger`或者任何其他你想使用的类库。但不要忘记，即使只是一个小小的处理器，你也应该注意使用高效的算法及设计模式，就像你在开发其他 java 程序中所做的一样。

### 3. 注册你的处理器
你可能会问 “怎样注册我的注解处理器到 javac ？”。你必须提供一个`.jar`文件。就像其他 .jar 文件一样，你将你已经编译好的注解处理器打包到此文件中。并且，在你的 .jar 文件中，你必须打包一个特殊的文件`javax.annotation.processing.Processor`到`META-INF/services`目录下。因此你的 .jar 文件目录结构看起来就你这样：
```
MyProcess.jar
	-com
		-example
			-MyProcess.class
	-META-INF
		-services
			-javax.annotation.processing.Processor
```
`javax.annotation.processing.Processor` 文件的内容是一个列表，每一行是一个注解处理器的全称。例如：
```
com.example.MyProcess
com.example.AnotherProcess
```