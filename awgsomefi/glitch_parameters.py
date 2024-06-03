import numpy as np
from awgsomefi.parameters.waveform import GlitchParams


xs = [165, 100, 182, 148, 126, 131]
#xs = np.interp(xs, [0, period], [0, 100])
ys = [0.22178592828010793, 0.18136811305398864, 0.12213574266556926, 0.06680186561657873, 0.1558895818917879, 0.06225573841626603]

default = GlitchParams.from_segments(xs, ys, 200)

# Good old
xs1 = [720.3488372093024, 1428.4883720930234, 2095.1162790697676, 2629.883720930233, 2876.511627906977, 3606.6279069767443]
ys1 = np.array([170.95162744751667, 230.7163555133212, 180.3870491995264, 103.95550545450219, 85.54353999067177, 52.88778875196533]) / 1000
period1 = 1797
xs1 = np.interp(xs1, [0, 4094], [0, 100])

version_one = GlitchParams(period1, xs1, ys1)


toffset = 6.403853216210059
xs2 = [258, 281, 239, 289, 231, 293]
ys2 = [0.23264335088371277, 0.09207924041826104, 0.19955751049724982, 0.08490539494865262, 0.1649369375276579, 0.22156726137808821]

version_two = GlitchParams.from_segments(xs2, ys2, 200)

# Good new
toffsetnew = 51
xsnew = [234, 299, 213, 255, 231, 273]
ysnew = [0.1678330206398118, 0.22072976436429156, 0.18231235398310666, 0.07846777771048857, 0.08652150089080485, 0.05256824131202503]

version_new = GlitchParams.from_segments(xsnew, ysnew, 250)
#periodnew = 1500
#print(periodnew)

toffsetpromise = 84
periodpromise = 1752
xspromise = [465.12842465753425, 1131.2671232876712, 1757.6712328767123, 2451.8578767123286, 2945.034246575343, 3510.6678082191784]
yspromise = np.array([180.20486177386047, 215.57675077124918, 126.74941706270315, 90.70129309192006, 57.81752498710887, 59.71370131121669])
yspromise /= 1000
xspromise = np.interp(xspromise, [0, 4094], [0, 100])

version_promising = GlitchParams(periodpromise, xspromise, yspromise)

toffset10x = 187
xs10x = [259, 223, 275, 166, 192, 246, 282]
ys10x = [0.09544221641441426, 0.09938208182932022, 0.2977872130867635, 0.18358277679224916, 0.0900131088054032, 0.28987825832888475, 0.2146252536166354]

version_10x = GlitchParams.from_segments(xs10x, ys10x, 200)

offset_newdouble = 168
xs_newdouble = [192, 195, 176, 150, 258, 212]
ys_newdouble = [0.11679642507026806, 0.099749695647689144, 0.1410706172566092, 0.32, 0.11077477847286256, 0.07934666817014926]

version_newdouble = GlitchParams.from_segments(xs_newdouble, ys_newdouble, 250)

offset_single = -157
xs_single = [89, 273, 167, 290, 183]
ys_single = [0.3181517551606869, 0.10225558596533249, 0.06627955969157984, 0.3832494827042806, 0.2126956344336903]

version_single = GlitchParams.from_segments(xs_single, ys_single, 250)

offset_newsingle = -15
xs_newsingle = [102, 158, 200, 80, 162]
ys_newsingle = [0.13674845354683793, 0.10976891796088271, 0.07658260203647976, 0.22734913319446387, 0.4]

version_newsingle = GlitchParams.from_segments(xs_newsingle, ys_newsingle, 250)


glitch_parameters: list[GlitchParams] = [
        default,
        version_one,
        version_two,
        version_new,
        version_promising,
        version_10x,
        version_newdouble,
        version_single,
        version_newsingle,
]
