from xml.dom import minidom

s="""<fipa-message act="inform">
	<sender>
		<agent-identifier>
			<name id="junction_0_0@127.0.0.1@127.0.0.1"/>
			<addresses>
				<url href="xmpp://junction_0_0@127.0.0.1@127.0.0.1"/>
			</addresses>
		</agent-identifier>
	</sender>
	<receiver>
		<agent-identifier>
			<name id="junction_0_1@127.0.0.1"/>
			<addresses>
				<url href="xmpp://junction_0_1@127.0.0.1"/>
			</addresses>
		</agent-identifier>
	</receiver>
	<content>junction_0_1@127.0.0.1|45|NS</content>
	<language>OWL-S</language>
	<ontology>init</ontology>
	<conversation-id>677446f6a372433aa7e281becde007eb</conversation-id>
</fipa-message>"""
# xmldoc = minidom.parse(s)
# itemlist = xmldoc.getElementsByTagName('sender')
# print itemlist
# print itemlist[0].attributes['name'].value
# for s in itemlist:
#     print(s.attributes['name'].value)
from xml.etree.ElementTree import XML, fromstring, tostring

root = fromstring(s)
print root

receiver = root.findall('receiver')[0]
agent_identifier = receiver.find('agent-identifier')
print agent_identifier
name_id = agent_identifier.find("name")
print name_id.attrib

content = root.find('content')
print content.text.split("|")