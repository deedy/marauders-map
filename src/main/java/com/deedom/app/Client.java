package com.deedom.app;

import java.net.InetSocketAddress;
import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.Props;
import akka.actor.UntypedActor;
import akka.io.Tcp;
import akka.io.Tcp.Bound;
import akka.io.Tcp.CommandFailed;
import akka.io.Tcp.Connected;
import akka.io.Tcp.ConnectionClosed;
import akka.io.Tcp.Received;
import akka.io.TcpMessage;
import akka.japi.Procedure;
import akka.util.ByteString;

public class Client extends UntypedActor {
	  
	  final InetSocketAddress remote;
	  final ActorRef listener;
	 
	  public Client(InetSocketAddress remote, ActorRef listener) {
	    this.remote = remote;
	    this.listener = listener;
	    
	    final ActorRef tcp = Tcp.get(getContext().system()).manager();
	    tcp.tell(TcpMessage.connect(remote), getSelf());
	  }
	 
	  @Override
	  public void onReceive(Object msg) throws Exception {
	    if (msg instanceof CommandFailed) {
	      listener.tell("failed", getSelf());
	      getContext().stop(getSelf());
	      
	    } else if (msg instanceof Connected) {
	      listener.tell(msg, getSelf());
	      getSender().tell(TcpMessage.register(getSelf()), getSelf());
	      getContext().become(connected(getSender()));
	    }
	  }
	 
	  private Procedure<Object> connected(final ActorRef connection) {
	    return new Procedure<Object>() {

	      public void apply(Object msg) throws Exception {
	        
	        if (msg instanceof ByteString) {
	          connection.tell(TcpMessage.write((ByteString) msg), getSelf());
	      
	        } else if (msg instanceof CommandFailed) {
	          // OS kernel socket buffer was full
	        
	        } else if (msg instanceof Received) {
	          listener.tell(((Received) msg).data(), getSelf());
	        
	        } else if (msg.equals("close")) {
	          connection.tell(TcpMessage.close(), getSelf());
	        
	        } else if (msg instanceof ConnectionClosed) {
	          getContext().stop(getSelf());
	        }
	      }
	    };
	  }
	  
	}