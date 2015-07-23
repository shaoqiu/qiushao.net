gradle使用
------
**create time: 2015-07-23; update time: 2015-07-23**

---------------------------------------------------------------

目前我们的项目组决定把开发工具转移到**android-studio**，以后的新项目都使用android-studio来开发。android-studio是使用**gradle**来进行构建的，所以有必要先熟悉一下 gradle。参考[官方文档](https://docs.gradle.org/current/userguide/userguide)

### 1. gradle 简介
引用官方的介绍：
> * A very flexible general purpose build tool like Ant.
> * Switchable, build-by-convention frameworks a la Maven. But we never lock you in!
> * Very powerful support for multi-project builds.
> * Very powerful dependency management (based on Apache Ivy).
> * Full support for your existing Maven or Ivy repository infrastructure.
> * Support for transitive dependency management without the need for remote repositories or pom.xml and ivy.xml files.
> * Ant tasks and builds as first class citizens.
> * Groovy build scripts.
> * A rich domain model for describing your build. 

从官方的介绍中我们大概可以知道 gradle 是一个非常灵活的构建工具，而且兼容现有的构建工具（ant, manven, Ivy），支持多工程构建，具有强大的依赖管理能力。

### 2. 基本概念
#### 2.1. project 和 task
在 gradle 中所有的东西都是基于两个基本概念：工程（project）和任务（task）。
使用 gradle 可以一次构建一个或多个工程。这里面的工程可以是各种各样的工程，可以是一个 JAR 包，可以是一个 web 应用，当然也可以是一个 android 应用。一个工程也可以不做任何构建工作，而用来完成部署工作，例如把应用部署到生产环境。
所有的工程都由一个或多个任务组成。一个任务就代表了在构建时会自动完成的一些工作。这些工作有可能是编译源文件，生成JAR包，生成文档，部署到生产环境等。
下面我们将会举几个简单的例子来说明gradle的使用。

#### 2.2 hello world
当我们运行gradle 命令时，gradle 会在当前目录寻找一个文件 `build.gradle`，我们叫它构建脚本，严格来说，应该叫它构建配置脚本。这个构建脚本定义了它的工程和它包含的任务。下面我们就以**hello world**工程来做个示范。这个工程只是打印了一行`hello world`而已。
创建一个文件，输入以下内容：
```
task hello {
    doLast {
        println 'Hello world!'
    }
}
```
然后在命令行中输入以下命令
```
D:\project\gradle>gradle -q hello
Hello world!
D:\project\gradle>
```
屏幕输出了一行`Hello world!`。这个构建定义了一个任务 hello ，这个任务有一个操作（action），当我们运行`gradle hello`时，gradle 就会执行 hello 这个任务，也就是执行你在任务中提供的操作。这些操作是将要执行 groovy 代码块。

#### 2.3. 定义任务的捷径
有一个快速定义任务的方法，看起来会更简洁：
```
task hello << {
    println 'Hello world!'
}
```
下面的例子都会采用这种形式。

#### 2.4. 构建脚本就是代码
gradle 的构建脚本中，你可以使用所有 groovy 语言的功能：
```
task upper << {
    String someString = 'mY_nAmE'
    println "Original: " + someString 
    println "Upper case: " + someString.toUpperCase()
}
```
运行gradle，结果如下：
```
D:\project\gradle>gradle -q upper
Original: mY_nAmE
Upper case: MY_NAME
D:\project\gradle>
```

#### 2.4. 任务依赖
正如你所猜的，我们可以声明一个任务叙事另一个任务：
```
task hello << {
    println 'Hello world!'
}
task intro(dependsOn: hello) << {
    println "I'm Gradle"
}
```
输出如下：
```
D:\project\gradle>gradle -q intro
Hello world!
I'm Gradle
D:\project\gradle>
```

需要说明的是任务的依赖声明可以不依赖任务的声明顺序。我们可以将 intro 任务放在 hello 任务声明之前，但需要做些修改，依赖的任务名需要用字符串的形式：
```
task intro(dependsOn: "hello") << {
    println "I'm Gradle"
}
task hello << {
    println 'Hello world!'
}
```

这个功能对于同时构建多个工程时是非常有用的。具体的后面再讨论。

#### 2.6. 默认任务
gradle 允许我们定义一个或多个默认任务，用以进行构建：
```
defaultTasks 'clean', 'run'

task clean << {
    println 'Default Cleaning!'
}

task run << {
    println 'Default Running!'
}

task other << {
    println "I'm not a default task!"
}
```
运行结果如下：
```
D:\project\gradle>gradle -q
Default Cleaning!
Default Running!
D:\project\gradle>
```

#### 2.7. 使用DAG进行配置
[gradle build lifecycle](https://docs.gradle.org/current/userguide/build_lifecycle.html)中介绍到，gradle 有一个配置阶段和一个执行阶段，配置阶段完成后，gradle 就可以知道所有将会执行的任务。gradle 提供了一个 hook 让我们可以获取这个信息。一个使用场景就是我们可以检查 release 任务是否在将会执行的任务中。根据这个，我们就可以给一些变量设置相应的值。例如：
```
task distribution << {
    println "We build the zip with version=$version"
}

task release(dependsOn: 'distribution') << {
    println 'We release now'
}

gradle.taskGraph.whenReady {taskGraph ->
    if (taskGraph.hasTask(release)) {
        version = '1.0'
    } else {
        version = '1.0-SNAPSHOT'
    }
}
```

### 3. 构建java工程
通过上面的例子，我们大概了解了工程，任务的概念。不过上面的例子中我们只是单纯的输出而已，并没有进行编译，打包，发布的实际工作。下面我们就来使用gradle构建一个java工程。在这个工程上演示各种实际用法。

#### 3.1. 

### 4. 构建android工程