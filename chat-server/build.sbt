name := "akka-socko-template"

version := "1.0"

scalaVersion := "2.10.3"

resolvers += "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"

libraryDependencies += "com.typesafe.akka" %% "akka-actor" % "2.2.3"

libraryDependencies += "com.typesafe.akka" %% "akka-slf4j" % "2.2.3"

libraryDependencies += "com.typesafe.akka" %% "akka-cluster" % "2.2.3"

libraryDependencies += "com.typesafe.akka" %% "akka-contrib" % "2.2.3"

libraryDependencies += "org.mashupbots.socko" %% "socko-webserver" % "0.4.1"
