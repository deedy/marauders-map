package dom.chatserver

/*
	Listener for cluster events
*/

import akka.actor._
import akka.cluster.Cluster
import akka.cluster.ClusterEvent._

class ClusterListener extends Actor with ActorLogging {
	def receive = {
		case state: CurrentClusterState =>
			log.info("Current members: {}", state.members)
		case MemberUp(member) =>
			log.info("Member is Up: {}", member)
		case UnreachableMember(member) =>
			log.info("Member detected as unreachable: {}", member)
		case _: ClusterDomainEvent => // ignore
	}
}