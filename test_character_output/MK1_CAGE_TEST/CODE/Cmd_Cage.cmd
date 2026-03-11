;-| Button Remapping |-----------------------------------------------------

[Remap]
x = x
y = y
z = z
a = a
b = b
c = c
s = s

;-| Default Values |-------------------------------------------------------
[Defaults]
; Default value for the "time" parameter of a Command. Minimum 1.
command.time = 15

; Default value for the "buffer.time" parameter of a Command. Minimum 1,
; maximum 30.
command.buffer.time = 1

;-| FATALITY |-----------------------------------------

[Command]
name = "Fatality1CAGE"
command = F, F, y
time = 30

[Command]
name = "Fatality2CAGE"
command = ~B, B, D, D+y
time = 40

[Command]
name = "Fatality2CAGE"
command = ~B, B, D, D, y
time = 40

;-| Super Motions |--------------------------------------------------------

[Command]
name = "Guarding"
command = /z
time = 1

[Command]
name =  "Green"
command = ~B,F+x
time = 14

[Command]
name =  "Green"
command = ~B,F,x
time = 14


[Command]
name =  "Shadowkick"
command = ~B,F+a
time = 14

[Command]
name =  "Shadowkick"
command = ~B,F,a
time = 14

[command]
name = "BallBreaker"
command = x+z
time = 5

;-| Double Tap |-----------------------------------------------------------
[Command]
name = "FF"     ;Required (do not remove)
command = F, F
time = 10

[Command]
name = "BB"     ;Required (do not remove)
command = B, B
time = 10

;-| 2/3 Button Combination |-----------------------------------------------
[Command]
name = "recovery";Required (do not remove)
command = a+b+c+x+y+z+s+D+U+F+D
time = 1

;-| Dir + Button |---------------------------------------------------------
[Command]
name = "down_a"
command = /$D,a
time = 1

[Command]
name = "down_b"
command = /$D,b
time = 1

;-| Single Button |---------------------------------------------------------
[Command]
name = "a"
command = a
time = 1

[Command]
name = "b"
command = b
time = 1

[Command]
name = "c"
command = c
time = 1

[Command]
name = "x"
command = x
time = 1

[Command]
name = "y"
command = y
time = 1

[Command]
name = "z"
command = z
time = 1

[Command]
name = "start"
command = s
time = 1

;-| Single Dir |------------------------------------------------------------
[Command]
name = "fwd" ;Required (do not remove)
command = $F
time = 1

[Command]
name = "downfwd"
command = $DF
time = 1

[Command]
name = "down" ;Required (do not remove)
command = $D
time = 1

[Command]
name = "downback"
command = $DB
time = 1

[Command]
name = "back" ;Required (do not remove)
command = $B
time = 1

[Command]
name = "upback"
command = $UB
time = 1

[Command]
name = "up" ;Required (do not remove)
command = $U
time = 1

[Command]
name = "upfwd"
command = $UF
time = 1

;-| Hold Button |--------------------------------------------------------------
[Command]
name = "hold_x"
command = /x
time = 1

[Command]
name = "hold_y"
command = /y
time = 1

[Command]
name = "hold_z"
command = /z
time = 1

[Command]
name = "hold_a"
command = /a
time = 1

[Command]
name = "hold_b"
command = /b
time = 1

[Command]
name = "hold_c"
command = /c
time = 1

[Command]
name = "hold_s"
command = /s
time = 1

;-| Hold Dir |--------------------------------------------------------------
[Command]
name = "holdfwd";Required (do not remove)
command = /$F
time = 1

[Command]
name = "holdback";Required (do not remove)
command = /$B
time = 1

[Command]
name = "holdup" ;Required (do not remove)
command = /$U
time = 1

[Command]
name = "holddown";Required (do not remove)
command = /$D
time = 1

;-| AI |------------------------------------------------------


[StateDef -1]

;AI
[State -1, AI]
type = VarSet
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = AIlevel != 0
trigger1 = 1
var(50) = 1

;============================================
;-------------------------------------------------------
[State -2, NO-FATALITY]
type = Varset
triggerall = 1
trigger1 = p2name = "MOTARO" || enemy,name = "MOTARO" 
trigger2 = p2name = "KINTARO-BOSS" || enemy,name = "KINTARO-BOSS" 
trigger3 = p2name = "SHAO KAHN-BOSS" || enemy,name = "SHAO KAHN-BOSS"
trigger4 = enemy,AuthorName = "OMEGAPSYCHO-BOSS"
trigger5 = enemy,AuthorName = "OMEGAPSYCHO-MKSecret"
trigger6 = enemy,AuthorName = "OMEGAPSYCHO-MKBoss"
v = 58
value = 0


;FATALITY TIME
[State 10000, 1]
type = Helper
triggerall = 1
triggerall = NumHelper(7000) = 0
triggerall = RoundState = 2
triggerall = p2statetype != A
triggerall = P2Life <= 1
triggerall = P2StateNo != 49999
triggerall = RoundNo >1
triggerall = var(58) >= 1
triggerall = var(55) = 0
trigger1 = NumEnemy = 1
trigger1 = NumPartner = 0
ID = 7000 
stateno = 7000
pos = 160, -140
postype = left
helpertype = normal
name = "FINISH_HIM_MODE" 
keyctrl = 0
ownpal = 1
size.xscale = 1
size.yscale = 1
;FATALITY TIME (BACKUP)
[State 10000, 2]
type = Helper
triggerall = 1
triggerall = NumHelper(7001) = 0
triggerall = RoundState = 2
triggerall = p2statetype != A
triggerall = P2Life <= 1
triggerall = P2StateNo != 49999
triggerall = RoundNo >1
triggerall = var(58) >= 1
triggerall = var(55) = 0
trigger1 = NumEnemy = 1
trigger1 = NumPartner = 0
ID = 7001 
stateno = 7001
pos = 160, -140
postype = left
helpertype = normal
name = "FINISH_HIM_MODE_BACKUP" 
keyctrl = 0
ownpal = 1
size.xscale = 1
size.yscale = 1

; Guarding
[State -1, Guarding]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = stateno != 120
triggerall = stateno != 140
triggerall = ctrl
triggerall = statetype = S || statetype = C
triggerall = command != "BallBreaker"
trigger1 = command = "Guarding"
value = 120

;==============================================
;-------------------------------------------------------------------

;STAND LOW PUNCH
[State -1 STAND LOW PUNCH]
type = ChangeState
triggerall = RoundState = 2
triggerall = command = "x"
triggerall = command != "BallBreaker"
triggerall = command != "holddown"
triggerall = command != "Green"
triggerall = statetype = S
triggerall = p2bodydist x >=10
trigger1 = Ctrl 
ignorehitpause = 1
value = 200

;STAND HIGH PUNCH
[State -1 STAND HIGH PUNCH]
type = ChangeState
triggerall = RoundState = 2
triggerall = command = "y"
triggerall = command != "Fatality2CAGE"
triggerall = command != "Fatality1CAGE"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = p2bodydist x >=10
trigger1 = Ctrl 
ignorehitpause = 1
value = 202

;UPPERCUT
[State -1,UPPERCUT]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "x" || command = "y"
triggerall = command != "Fatality2CAGE"
triggerall = command != "Fatality1CAGE"
triggerall = command != "BallBreaker"
triggerall = command != "Green"
triggerall = command = "holddown"
triggerall = statetype != A
trigger1 = Ctrl 
ignorehitpause = 1
value = 210

;STRONG PUNCH CLOSE
[State -1, STRONG PUNCH CLOSE]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "y"
triggerall = command != "Fatality2CAGE"
triggerall = command != "Fatality1CAGE"
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = p2bodydist x < 10
trigger1 = Ctrl 
ignorehitpause = 1
value = ifelse(p2statetype=A,202,240)

;JUMP PUNCH
[State -1,JUMP PUNCH]
type = ChangeState
triggerall = RoundState = 2
triggerall = command = "x" || command = "y"
triggerall = statetype = A
trigger1 = Ctrl 
ignorehitpause = 1
value = 245

;JUMP KICK NEUTRAL
[State -1,JUMP KICK NEUTRAL]
type = ChangeState
triggerall = RoundState = 2
triggerall = Vel X = 0
triggerall = command = "a" || command = "b"
triggerall = statetype = A
trigger1 = Ctrl 
ignorehitpause = 1
value = 248

;JUMP KICK 
[State -1,JUMP KICK]
type = ChangeState
triggerall = RoundState = 2
triggerall = Vel X > 0 || Vel X < 0
triggerall = command = "a" || command = "b"
triggerall = statetype = A
trigger1 = Ctrl 
ignorehitpause = 1
value = 250

;LOW KICK NEUTRAL
[State -1,LOW KICK NEUTRAL]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = command != "holdback"
triggerall = command != "Shadowkick"
triggerall = statetype = S
triggerall = p2bodydist x >= 10
trigger1 = Ctrl 
ignorehitpause = 1
value = 254

;HIGH KICK NEUTRAL
[State -1,HIGH KICK NEUTRAL]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = command != "holdback"
triggerall = statetype = S
triggerall = p2bodydist x >= 10
trigger1 = Ctrl 
ignorehitpause = 1
value = 255

;CLOSE KICK for low kick
[State -1,CLOSE KICK]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "a"
triggerall = command != "holddown"
triggerall = command != "holdback"
triggerall = command != "Shadowkick"
triggerall = statetype = S
triggerall = p2bodydist x < 10
trigger1 = Ctrl 
ignorehitpause = 1
value = ifelse(p2statetype=A,254,257)

;CLOSE KICK for High kick
[State -1,CLOSE KICK]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "b"
triggerall = command != "holddown"
triggerall = command != "holdback"
triggerall = command != "Shadowkick"
triggerall = statetype = S
triggerall = p2bodydist x < 10
trigger1 = Ctrl 
ignorehitpause = 1
value = ifelse(p2statetype=A,255,257)

;CROUCH KICK
[State -1,CROUCH KICK]
type = ChangeState
triggerall = RoundState = 2
triggerall = command = "a" || command = "b"
triggerall = command = "holddown"
triggerall = command != "Shadowkick"
triggerall = statetype = C
trigger1 = Ctrl 
ignorehitpause = 1
value = 259

;LIEDOWN KICK
[State -1,LIEDOWN KICK]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "a"
triggerall = command != "Shadowkick"
triggerall = command = "holdback"
triggerall = statetype = S
trigger1 = Ctrl 
ignorehitpause = 1
value = 260

;BACK STRONG KICK
[State -1, BACK STRONG KICK]
type = ChangeState
triggerall = RoundState = 2
triggerall = command = "b"
triggerall = command = "holdback"
triggerall = statetype = S
trigger1 = Ctrl 
ignorehitpause = 1
value = 270

;********************************************************
;************************POWERS************************
;********************************************************

;GREEN BOLT
[State -1,GREEN BOLT]
type = ChangeState
triggerall = var(50) = 0
triggerall = NumHelper(331)= 0
triggerall = NumHelper(332)= 0
triggerall = RoundState = 2
triggerall = command = "Green"
trigger1 = ctrl && statetype != A
trigger2 = stateno = 251 && statetype = A
trigger3 = stateno = 52 && statetype = A
ignorehitpause = 1
value = 330

;SHADOW KICK
[State -1, SHADOW KICK]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "Shadowkick"
trigger1 = ctrl && statetype != A
trigger2 = stateno = 251 && statetype = A
trigger3 = stateno = 52 && statetype = A
trigger4 = stateno = 330 && time >32 && p2stateno = [5020,5030]
ignorehitpause = 1
value = 335

;BALL BREAKER
[State -1, BALL BREAKER]
type = ChangeState
triggerall = var(50) = 0
triggerall = RoundState = 2
triggerall = command = "BallBreaker"
trigger1 = ctrl && statetype != A
trigger2 = stateno = [120,141]
ignorehitpause = 1
value = 340

;THROW CAGE
[State -1,THROW]
type = ChangeState
triggerall = RoundState = 2
triggerall = command = "x"
triggerall = statetype != A
triggerall = p2bodydist x <= 10
trigger1 = Ctrl 
ignorehitpause = 1
value = 410

;*****************************************************************************
;****************************FATALITY*************************************
;*****************************************************************************

;FATALITY # 1 CAGE
[State -1, FATALITY # 1 CAGE]
type = ChangeState
triggerall = P2Dist X < 250
triggerall = var(55) >= 1
triggerall = RoundState = 2
triggerall = p2stateno = 49999
triggerall = command = "Fatality1CAGE"
triggerall = statetype != A
trigger1 = Ctrl 
trigger2 = stateno = 130
trigger3 = stateno = 131
ignorehitpause = 1
value = 500

;FATALITY # 2 CAGE
[State -1, FATALITY # 2 CAGE]
type = ChangeState
triggerall = P2Dist X < 250
triggerall = var(55) >= 1
triggerall = RoundState = 2
triggerall = p2stateno = 49999
triggerall = command = "Fatality2CAGE"
triggerall = statetype != A
trigger1 = Ctrl 
trigger2 = stateno = 130
trigger3 = stateno = 131
ignorehitpause = 1
value = 600
















































































;****************************************************************************
;****************************************************************************
;************   AI  ***********************************************************
;****************************************************************************
;****************************************************************************
; Guarding
[State -1, Guarding]
type = ChangeState
triggerall = var(50) = 1
triggerall = RoundState = 2
triggerall = life>1
triggerall = stateno != [5100,5150]
triggerall = NumHelper(7000) = 0
triggeral = P2StateNo != 49999
triggerall = Movetype = I
triggerall = p2Movetype != I || enemynear,movetype != I
triggerall = p2Movetype = A || enemynear,movetype = A
triggerall = p2Statetype != C
triggerall = stateno != 120
triggerall = stateno != 131
triggerall = stateno != 140
triggerall = stateno != 25
triggerall = ctrl
triggerall = statetype != A
trigger1 = P2Dist X <200
trigger1 = p2movetype = A
trigger1 = p2statetype = S
trigger2 = enemy, NumProj >= 1
trigger2 = P2Dist X <=120
trigger2 = statetype = S
trigger3 = P2Dist X <20
trigger3 = p2movetype = A
trigger3 = p2statetype = S
trigger4 = enemy, NumProj >= 1
trigger4 = Random <=500
trigger4 = P2Dist X >=100
trigger4 = statetype = S
ignorehitpause = 1
value = 120
; Crouch Guarding
[State -1, Guarding]
type = ChangeState
triggerall = var(50) = 1
triggerall = RoundState = 2
triggerall = life>1
triggerall = stateno != [5100,5150]
triggerall = NumHelper(7000) = 0
triggeral = P2StateNo != 49999
triggerall = p2Movetype != I || enemynear,movetype != I
triggerall = p2Movetype = A || enemynear,movetype = A
triggerall = p2Statetype != S
triggerall = stateno != 120
triggerall = stateno != 130
triggerall = stateno != 140
triggerall = stateno != 25
triggerall = ctrl
triggerall = statetype != A
trigger1 = P2Dist X <200
trigger1 = p2movetype = A
trigger1 = p2statetype = C
trigger2 = enemy, NumProj >= 1
trigger2 = P2Dist X <=120
trigger2 = statetype = C
trigger3 = P2Dist X <20
trigger3 = p2movetype = A
trigger3 = p2statetype = C
trigger4 = enemy, NumProj >= 1
trigger4 = Random <=500
trigger4 = P2Dist X >=100
trigger4 = statetype = C
ignorehitpause = 1
value = 131

;JUMP
[State -1,JUMP]
type = ChangeState
triggerall = var(50) = 1
triggerall = life>1
triggerall = Random < AILevel *12
triggerall = RoundState = 2
triggerall = statetype != A
triggerall = Ctrl || stateno = [120,140]
triggerall = stateno != 40
triggerall = stateno != 45
triggerall = stateno != 50
triggerall = stateno != 51
triggerall = stateno != 52
trigger1 = P2Dist X <200
trigger1 = P2statetype = A
trigger1 = P2movetype = A
trigger2 = enemy, NumProj >= 1
trigger2 = P2Dist X >100
ignorehitpause = 1
value = 40
[State -1,JUMP]
type = ChangeState
triggerall = var(50) = 1
triggerall = life>1
triggerall = Random < AILevel *9
triggerall = RoundState = 2
triggerall = statetype != A
triggerall = P2movetype = A
triggerall = enemynear,movetype = I
triggerall = P2Dist X <200
triggerall = Ctrl || stateno = [120,140]
trigger1 = enemynear,stateno = 40
trigger2 = enemynear,stateno = 45
trigger3 = enemynear,stateno = 50
trigger4 = enemynear,stateno = 51
trigger5 = enemynear,stateno = 52
ignorehitpause = 1
value = 40
[State -1,JUMP]
type = ChangeState
triggerall = var(50) = 1
triggerall = life>1
triggerall = Random < AILevel *9
triggerall = RoundState = 2
triggerall = statetype != A
triggerall = P2movetype = A
triggerall = enemynear,movetype = I
triggerall = P2Dist X <200
triggerall = Ctrl || stateno = [120,140]
trigger1 = stateno = 20
trigger1 = P2BodyDist X >= 130
trigger1 = Random < 150
trigger1 = enemy, numproj >= 1
trigger2 = stateno = 20
trigger2 = P2bodydist X <= 60
trigger2 = BackEdgeBodyDist <= 10
trigger2 = Random < 600
trigger2 = p2statetype = L
trigger3 = stateno = 20
trigger3 = P2BodyDist X <= 100
trigger3 = Random < 50+(enemynear,hitdefattr=SCA,HT)*250
trigger3 = enemynear,hitdefattr = SCA,NT,ST,HT
ignorehitpause = 1
value = 40




;STAND 1,2,3, PUNCH
[State -1 STAND LOW PUNCH]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = statetype = S
triggerall = life>1
triggerall = p2bodydist x = [0,35]
triggerall = p2statetype != L
triggerall = p2statetype != C
triggerall = P2movetype != A
triggerall= Random < AILevel * 10
trigger1 = Ctrl || stateno = [120,140]
ignorehitpause = 1
value = ifelse(random<=500,200,202)

;THROW AI
[State -1,THROW]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = Random < AILevel *12
triggerall = p2bodydist x <= 10
triggerall = life>1
triggerall = stateno != [5100,5150]
triggerall = movetype = I
triggerall = statetype = S
triggerall = p2statetype != L
triggerall = p2statetype != A
triggerall = p2movetype != H
trigger1 = Ctrl || stateno = [120,140]
ignorehitpause = 1
value = 410

;UPPERCUT
[State -1,UPPERCUT]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = Random < AILevel *10
triggerall = statetype != A
triggerall = p2statetype != L
triggerall = p2movetype != H
triggerall = Ctrl || stateno = [120,140]
triggerall = p2life>1
triggerall = stateno != [5100,5150]
triggerall = p2stateno != [5100,5150]
trigger1 = p2bodydist x = [0,30]
trigger1 = p2statetype != C
trigger1 = p2movetype = A
trigger1 = statetype = C
trigger2= p2statetype = A
trigger2 = p2bodydist X <40
trigger2 = p2bodydist Y >-120
trigger2 = enemynear,Vel X >0
trigger3 = p2statetype = A
trigger3 = p2bodydist X <40
trigger3 = p2bodydist Y >-140
trigger3 = enemynear,Vel X >0
trigger4 = p2statetype = A
trigger4 = p2bodydist X <40
trigger4 = enemynear,Vel X <=0
trigger5 = P2Dist X <20
trigger5 = p2stateno = 345
ignorehitpause = 1
value = 210

;CLOSE ATTACK 
[State -1,CLOSE ATTACK ]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = Random < AILevel *12
triggerall = command != "holddown"
triggerall = statetype = S
triggerall = p2statetype = S
triggerall = p2life>1
triggerall = p2statetype != L
triggerall = stateno != [5100,5150]
triggerall = P2stateno != [5100,5150]
triggerall = p2bodydist x <= 10
trigger1= Ctrl
trigger1 = P2stateno = [120,140]
trigger2 = Ctrl
trigger2 = enemynear,Vel X = 0
trigger2 = p2movetype != A
trigger3 = Ctrl
trigger3 = enemynear,Vel X < 0
trigger3 = p2movetype = I
trigger4 = Ctrl
trigger4 = p2movetype = A
trigger4 = enemynear,hitdefattr = SCA,SA,SP,HA,HP
trigger5 = stateno = [120,140]
trigger5 = p2movetype = I
ignorehitpause = 1
value = ifelse(random<=500,240,257)


;JUMP PUNCH
[State -1,JUMP PUNCH]
type = ChangeState
triggerall = var(50) = 1
triggerall = RoundState = 2
triggerall = Random < AILevel *12
triggerall = Vel X !=0
triggerall = p2dist x = [0,100]
triggerall = statetype = A || Stateno = 50
triggerall = p2Statetype = A
trigger1 = Ctrl
ignorehitpause = 1
value = 245

;JUMP KICK 
[State -1,JUMP KICK]
type = ChangeState
triggerall = var(50) = 1
triggerall = RoundState = 2
triggerall = Vel X !=0
triggerall = Random < AILevel *12
triggerall = p2dist x <300
triggerall = statetype = A || Stateno = 50
triggerall = p2Statetype != A
trigger1= Ctrl
ignorehitpause = 1
value = 250

;JUMP KICK NEUTRAL
[State -1,JUMP KICK NEUTRAL]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = Random < AILevel *12
triggerall = Vel X = 0
triggerall = p2dist x = [0,70]
triggerall = statetype = A || Stateno = 50
triggerall = p2Statetype = A
trigger1 = Ctrl 
ignorehitpause = 1
value = 248

;LIEDOWN KICK
[State -1,LIEDOWN KICK]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = Random < AILevel *11
triggerall = statetype != A
triggerall = Ctrl || stateno = [120,140]
triggerall = p2bodydist x = [0,100]
trigger1 = p2statetype = S
trigger1 = p2movetype = H
trigger2 = p2statetype =S
trigger2 = p2stateno = [120,140]
trigger3 = p2statetype = S
trigger3 = p2movetype = A
trigger3 = enemynear,hitdefattr = SCA,NP,SP
trigger4 = p2statetype = S
trigger4= enemynear,Vel X <0
trigger4 = p2movetype = I
trigger5 = p2statetype = S
trigger5 = p2movetype = I
trigger5 = movetype = I
trigger5 = Random >800
ignorehitpause = 1
value = 260

;LOW KICK NEUTRAL
[State -1,LOW KICK NEUTRAL]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = Random < AILevel *10
triggerall = RoundState = 2
triggerall = statetype = S
triggerall = p2bodydist x >= 10
triggerall = Ctrl || stateno = [120,140]
triggerall = p2statetype != L
triggerall = p2bodydist x = [0,60]
triggerall = movetype = I
trigger1 = p2movetype = I
trigger1 = p2statetype != A
trigger1 = Random <300
trigger2 = enemynear, Stateno = [5030,5050]
trigger2 = enemynear, Pos y >-120
trigger3 = p2statetype = A
trigger3 = p2movetype != A
trigger3 = enemynear, Vel x = 0
trigger3 = enemynear, Pos y >-120
ignorehitpause = 1
value = 254

;HIGH KICK NEUTRAL
[State -1,HIGH KICK NEUTRAL]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = Random < AILevel *10
triggerall = RoundState = 2
triggerall = statetype = S
triggerall = p2bodydist x >= 10
triggerall = Ctrl || stateno = [120,140]
triggerall = p2statetype != L
triggerall = p2statetype != A
triggerall = p2bodydist x = [0,70]
triggerall = movetype = I
trigger1 = p2movetype = I
trigger1 = p2statetype != A
trigger1 = Random >700
trigger2 = enemynear, Stateno = [5030,5050]
trigger2 = enemynear, Pos y <=-120
trigger2 = Random >700
trigger3 = p2statetype = A
trigger3 = p2movetype = A
trigger3 = enemynear, Vel x = 0
trigger3 = enemynear, Pos y <=-120
trigger3 = Random >700
ignorehitpause = 1
value = 255

;BACK STRONG KICK
[State -1, BACK STRONG KICK]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = Random < AILevel *10
triggerall = RoundState = 2
triggerall = statetype = S
triggerall = p2bodydist x >= 10
triggerall = Ctrl || stateno = [120,140]
triggerall = p2statetype != L
triggerall = p2statetype != A
triggerall = p2bodydist x = [0,70]
triggerall = movetype = I
trigger1 = p2movetype = I
trigger1 = p2statetype != A
trigger1 = Random = [400,700]
trigger2 = enemynear, Stateno = [5030,5050]
trigger2 = enemynear, Pos y <=-120
trigger2 = Random <400
trigger3 = p2statetype = A
trigger3 = p2movetype = A
trigger3 = enemynear, Vel x = 0
trigger3 = enemynear, Pos y <=-120
trigger3 = Random <400
ignorehitpause = 1
value = 270



;*************************SP. COMMANDS*******************************

;LIEDOWN KICK & LOW NEUTRAL KICK & CROUCH LOW KICK
[State -1,LIEDOWN KICK]
type = ChangeState
triggerall = var(50) = 1
triggerall = life>1
triggerall = p2life>1
triggerall = stateno != [5100,5150]
triggerall = RoundState = 2
triggerall = random = [600,999]
triggerall = statetype != A
triggerall = statetype != L
triggerall = p2statetype != L
triggerall = p2movetype != H
triggerall = p2dist X = [-40,60]
trigger1 = ctrl
ignorehitpause = 1
value = ifelse(random<=600,260,ifelse(random>600,254,259))

;JUMP ATTACK 1
[State -1,JUMP KICK]
type = ChangeState
triggerall = var(50) = 1
triggerall = life>1
triggerall = Random =[0,700]
triggerall = RoundState = 2
triggerall = Vel X > 0 || Vel X < 0
triggerall = statetype = A
triggerall = movetype = I
triggerall = P2Dist X <150
triggerall = enemy, NumProj <= 0
trigger1 = ctrl
ignorehitpause = 1
value = ifelse(random<=800,250,245)

;JUMP ATTACK 2
[State -1,JUMP KICK]
type = ChangeState
triggerall = var(50) = 1
triggerall = life>1
triggerall = Random =[300,999]
triggerall = RoundState = 2
triggerall = Vel X > 0
triggerall = statetype = A
triggerall = movetype = I
triggerall = P2Dist X <170
triggerall = enemy, NumProj >= 1
trigger1 = ctrl
ignorehitpause = 1
value = ifelse(random<=800,250,245)

;JUMP ATTACK NEUTRAL 2
[State -1,JUMP ATTACK]
type = ChangeState
triggerall = var(50) = 1
triggerall = life>1
triggerall = Random =[200,999]
triggerall = RoundState = 2
triggerall = Vel X = 0
triggerall = statetype = A
triggerall = P2statetype = A
triggerall = Enemynear,statetype = A
triggerall = movetype = I
triggerall = P2Dist X <70
trigger1 = ctrl
ignorehitpause = 1
value = 248 


;****************************************************************************
;***************************A.I. POWERS*************************************
;****************************************************************************

;GREEN BOLT
[State -1,FIREBALL]
type = ChangeState
triggerall = var(50) = 1
triggerall = NumHelper(331)= 0
triggerall = NumHelper(332)= 0
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = Random < AILevel *12
triggerall = p2name != "MOTARO"
triggerall = p2name != "JADE MK2"
triggerall = life>1
triggerall = statetype != A
triggerall = statetype != L
triggerall = stateno != 330
trigger1       = Ctrl
trigger1       = p2movetype = A
trigger1       = p2statetype = A
trigger1       = enemynear,vel x <=0
trigger1       = p2bodydist X > 80
trigger1       = p2bodydist Y >-120
trigger2       = Ctrl
trigger2       = enemynear, Stateno = 50
trigger2       = enemynear, anim = 43 || enemynear, anim = 41
trigger2       = p2bodydist X > 180
trigger2       = p2bodydist Y >-120
trigger3       = Ctrl
trigger3       = enemynear,vel x = 0
trigger3       = p2bodydist X > 190
trigger3       = p2movetype = A
trigger3       = p2statetype != A
trigger3       = enemy, NumProj =0
trigger3       = random <= 400 
trigger4       = Ctrl
trigger4       = enemynear,vel x <0
trigger4       = enemynear, Stateno = [5030,5050]
trigger4       = p2bodydist X > 100
trigger4      = random <=400 
trigger5       = Ctrl || stateno = [120,140]
trigger5       = p2movetype = A
trigger5       = p2bodydist X > 100
trigger6       = Ctrl
trigger6       = enemynear,vel x = 0
trigger6       = p2bodydist X > 250
trigger6       = enemy, NumProj >=1
trigger6       = random <= 200 
trigger7       = Ctrl
trigger7       = P2stateno = [123456,123458]
ignorehitpause = 1
value = 330

;SHADOW KICK
[State -1,SHADOW KICK]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = Random < AILevel *11
triggerall = life>1
triggerall = RoundState = 2
triggerall = statetype != A
triggerall = statetype != L
triggerall = p2statetype != L
triggerall = enemy, NumProj = 0
trigger1       = Ctrl
trigger1       = enemynear,vel x <0
trigger1       = p2bodydist X <100
trigger1       = p2statetype != C
trigger2       = stateno = 330 
trigger2       = time >32
trigger2       = p2movetype = H
trigger3       = Ctrl
trigger3       = p2bodydist X <120 
trigger3       = p2stateno = [5020,5045]
trigger4       = p2movetype = I
trigger4       = Ctrl || stateno = [120,140]
trigger4       = random <= 300 
trigger4       = p2bodydist X >100 
trigger4       = p2bodydist X <150 
trigger5       = Ctrl
trigger5       = P2stateno = [123456,123458]
ignorehitpause = 1
value = 335

;BALL BREAKER
[State -1, BALL BREAKER]
type = ChangeState
triggerall = var(50) = 1
triggerall = stateno !=210
triggerall = p2Stateno != 345
triggerall = RoundState = 2
triggerall = Random < AILevel *11
triggerall = P2Name != "GORO"
triggerall = P2Name != "KINTARO"
triggerall = P2Name != "MOTARO"
triggerall = P2Name != "SHAO KAHN"
triggerall = P2Name != "JOHNNY CAGE MK1"
triggerall = var(4) = 0
triggerall = life>1
triggerall = statetype != L
triggerall = stateno != [5100,5150]
triggerall = stateno != 340
triggerall = statetype != A
triggerall = movetype != H
triggerall = p2movetype != H
trigger1 = P2Dist X <40
trigger1 = BackEdgeDist < 60
trigger1 = Ctrl || stateno = [120,140]
value = 340

;****************************FATALITY-A.I.******************

;FATALITY CAGE
[State -1, FATALITY]
type = ChangeState
triggerall = P2Dist X < 250
triggerall = var(50) = 1
triggerall = var(55) >= 1
triggerall = stateno !=210
triggerall = RoundState = 2
triggerall = Random < AILevel *10
triggerall = RoundState = 2
triggerall = statetype != A
triggerall = movetype = I
triggerall = enemynear,stateno = 49999 || p2stateno = 49999 
trigger1 = Ctrl
value = ifelse(random<=500,500,600)




