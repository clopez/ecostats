#!/usr/bin/python
#
# (P) Sergiusz Pawlowicz 2008
# (C) GPLv3
# http://code.google.com/p/ecostats/
#
# grapefriut color manipulation module:
# http://code.google.com/p/grapefruit/
import grapefruit
#
alphabet = 'abcdefghkmnopqrstuvwxyz'
#
# pairs are prepared by myself, so are maybe personal a little bit
pairs=	[ 
	["#66CCFF","#0066FF"], # a
	["#99CC99","#336600"], # b
	["#9ACD32","#556B2F"], # c
	["#AFEEEE","#40E0D0"], # d
	["#87CEEB","#1E90FF"], # e
	["#DEB887","#8B4513"], # f
	["#FFD700","#FF4500"], # g
	["#DC143C","#B22222"], # h
	["#D8BFD8","#7B68EE"], # i
	["#FFA07A","#FF4500"], # j
#	["",""],
	]
# generate CSS code with several color grades
letter = 0
for pair in pairs:
	number = 0
	color1 = grapefruit.Color.NewFromHtml(pair[0])
	color2 = grapefruit.Color.NewFromHtml(pair[1])
	for i in color1.Gradient(color2, 10):
		print "p.state%s%s {" % (alphabet[letter] , str(number))
		print " background: %s;" % i.html
		print "}"
		number += 1
	letter += 1
# the end.
