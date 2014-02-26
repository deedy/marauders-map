package dom.chatserver

sealed trait Event
case class ChatMessage(message : String) extends Event