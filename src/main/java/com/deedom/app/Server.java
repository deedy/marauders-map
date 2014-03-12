package com.deedom.app;

import java.util.*;
import java.net.InetSocketAddress;
import akka.actor.*;
import akka.io.Tcp.*;
import akka.io.TcpMessage;


public class Server extends UntypedActor {

	final String host_address = "localhost";
	final int port = 3000;
	
	@Override
	public void preStart () throws Exception {
		// get a reference to the system's tcp actor
		final ActorRef tcp = Tcp.get(getContext().system()).manager();
		tcp.tell(TcpMessage.bind(getSelf(), new InetSocketAddress("localhost", 3000), 100), getSelf());
	}
	
	@Override
	public void onReceive(Object msg) throws Exception {
	if (msg instanceof Bound) {
	manager.tell(msg, getSelf());
	
	} else if (msg instanceof CommandFailed) {
	getContext().stop(getSelf());
	
	} else if (msg instanceof Connected) {
	final Connected conn = (Connected) msg;
	manager.tell(conn, getSelf());
	final ActorRef handler = getContext().actorOf(
	Props.create(SimplisticHandler.class));
	getSender().tell(TcpMessage.register(handler), getSelf());
	}
	}

}