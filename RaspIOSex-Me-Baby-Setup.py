#!/usr/bin/env python3
# RaspIOSex Me Baby - universal installer (Windows / macOS / Linux).
#
# One file: it detects the machine it is running on and installs the
# matching version of the app - the right install folder, launchers,
# shortcuts and uninstaller for that OS. The app itself is embedded
# below as a compressed payload; nothing else is needed.
#
#   Install:    python3 RaspIOSex-Me-Baby-Setup.py
#   Uninstall:  python3 RaspIOSex-Me-Baby-Setup.py --uninstall
# (On Windows use "py -3" instead of "python3". Python 3.9+ required.)

import base64
import os
import platform
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

APP_NAME = "RaspIOSex Me Baby"
APP_VERSION = "1.0.0"
APP_FILE = "raspiosex_me_baby.py"
PUBLISHER = "Delukz"

PAYLOAD_B64 = (
    "eNrNPdty20aW7/yKDrxTAmISujmOlxNlSrblRDOWpZXk3GQVCyRAEREIIGhAF2s5NU9bu69b+w37"
    "YfMley7dQONCSkrsqvWDRQLdp0+fPvc+3XzyxXohs/VxGK8H8ZVIb/NZEm/3LMvqHXsy3T88CW7E"
    "QSBeeuNb8c9//I/wxCRLpBykkZdPk2wu7B/D2E+upVgXc29yeAJ/34ZxceOIWRClQSbymZcPez0h"
    "Nl3xOrmOo8TzpUDo4yDLbsVRKKDXNEvm0DQQh2/e7L/a331bb+GrjmIaBD7Agn82tpbePBCJHEWh"
    "zOkdwUim03ASelEdxv7cuwB8ChlIxwUYWyY+Yy8KYm8vn8ygCSET5rJC5rsw/74YiyyIAg/6Cy/2"
    "RRGn3uRSQkOF0LgIo3wQxuKX/SMhizRNspyIFiciuMkzD7p8DFORZslF5s1FDPgGPuGy7Yo9bDGB"
    "QXEGbji/cG8+igQo6OVhfDGQtzIPACuchDHUT7/okRxxPQujgHG5CrJwegv9aBon3+8Otr56LmBy"
    "gHABUGJRUi/1pEQUnrniTeTJWcAY8EB5Ais+D2HNT16LiZf5fRGEOdII+CHyingyw0EU3ZJMXMNb"
    "RgGBlGheZ2EeZDjMVzAM8I2XI8dchykSkyBTVzGFKaipJmkeJrEU9pvd0+0tGPgGPvTF3k+nz4Bm"
    "vT2YI7ArzVEKmScZrD4M5QkrCseZl91aYppEPuAVA/VxKtAaRktTIRNC73qWAMHyJIkuQ14peNlH"
    "duTZ4yqrqeFLmXu3EodIYiBb5E0CxQdhDK+iiFHp/VoAL/rAKbhuNI5Cwy5bCjnJwhRI4GVA6XgS"
    "FcwIvZPwI1LNvwhyYWfBJJnPgxjeteTl+bPBGHB+HcjLPEGcJ7nY2th6TiT3nSFQupQZW3GTI8Tf"
    "N93t5+K7l+Ipc+QkB9j4Wvz9ufv1M36jpvz3DXdrE54AqB3hjZMiFy/cbWySBt4lUQSmE/oBzXFz"
    "A98w6q44hSfWmyKKLHHlZaEX81wB1Di8QClEwmE3XI1rL4Nlvp4FuHiTWRICYa+TIvLFOMORWuB7"
    "PZMlQSp/K8IsAErlQ/EC283DOJwX877YpMkCX0ZehsMaJO3Z21v4EibgRQ6jrJYHGuoFgu95wIxT"
    "pKgY4rxvIt/LAqBGjlpAjAPQiMgTtxXtYegpShXgfFTAyyPSsAg29hF3xapaTaSgHhQSUukHV/fZ"
    "dv/1qUuquRfOSbfMADAA0F9/lUmsP0cf557+nEj9SWvt6jvoTQOCnBV5GJXfijGoqkkgy/4gmfpj"
    "7mUoq/prkQH/j11cikDm+iloO2rU2z06Gr3bPdgDTrJahsXq/bB3fLJ/+A7fbrob7obVe/n+9Xd7"
    "p6OXP5/uncBjWP4v4b+N5h/xpMYZIGkZSkfJw0A2P5SXvd7hyejt/snp6P3xWxxlluepHK6v63WS"
    "bqYFLA1d4JF1ZVRGqAlAjpEuYX47unrmIpmt3t7pq+/3jke7R/smPA96X4AeK8YEBJgjketsWwZh"
    "sh4QVuvajKzDcgC1YEFf7p7sjV7vHwOsRLqpl89cP8xi0M+2/u6NJf61RyMk6WjkOL23+y8bnX5N"
    "wtjWwPqVJnSQAB1NFQRomUhopCa1siHPARr3Tn4+Od07gJaarVzW3LaD67KmHIO1vlh77WXXYYyf"
    "yDdY6x3svvp+/92e2Re8B1Dmge24UXIdZDYM8EQMPtk/AHYyR9XLbon8tMB7fjAVF2M7Js0rQM/k"
    "RRaLGGwcs+uXYpsbTef5SIKWL5uGU2gG6uUdWBV+YgCwivgyBh4V2MUyQU+tOx7P3ZouUALsu3jY"
    "X4BdBpZyLB4siCUonRGwkrTVcCghZCerJWXWAMtarr5TIQJcMPcuAwKB1v8GhSK53DnNisDhUcZe"
    "HOOCcac0C+PctnYskNHnLxzj2dQSd1oRLMTVnZL6hSDt1zJxWoj7ZG+VlbacewaxRJdt8LsNg2lh"
    "a+agPow4jAeoRhpahp0EjeZQaSK7MmmwtMHNhL28JYgTAVF7jADwCFWLDaq05KLfQELqqtU95r/Y"
    "rA/M7IFnIXfurPcyyAa7F2ADrSEyR0noddCo1oJHJxerAQ++gpcZg7fxW1/k4TwAQ7/zfMMRnhRZ"
    "iyERQ5c0pp0BCM8HefWBin5gW0U+HbywHDUprVpJXTG2PoyHLJQG6HeQGOwg2/fBPI+DaMfCppaa"
    "PBg67Z4z3h47zmCOgOMyVxwTRuytoqIiJzMPYhdNJHmg8xTIh4PCIlmgzLLc+n9H1zwBYw/Y1KiC"
    "bgPySeYqRFzgDtt6Bd4HIDJ4G8QX+cxysNmGU4LyUU52xEb5gNAiJIAUoLqvxxYNP62Gp2YYNwgU"
    "6Ppz/DeZgQYCoGqxNze2npHt3XrmtNqiJkty7tKGhP/In2u9mboUHtjUsQ2WpvV0R4ARXdYERiY6"
    "do+agm+8w2DIbRDr69y8G0cvQ4v+BCXUxq7QestBDhrQo682xECUz7sHVOruQybEHbH2YijO7gDy"
    "4lzcQd/Fn+BFaQkQM2dhgWTE/o4Ff6dRIWdKwzZhB5EMhg8ftTlKKZaBv2JABsWfwQCAG4PRDnMR"
    "ypNjWiJ8wCIvZx6EmaNkyjKPQlmKNkekWrhnQGLlvbrcS42mxUE7H8D3hD1+4RY1Lq84nAezsjaL"
    "L2NvzdrTe1h7NVu3WXrmFqnvdfPzPbzcvYR1zp17NzZRqb/pLP70wEVUSzUDfXLjhxeo55Sa9uSl"
    "DXp1nua4tFOviHLSyWqhZDGdhjdIJQs4WDVYnFtIFfWNWFJonZvdVjS6oqUM47TASd3xMIs7hgkz"
    "sxxX5hBnKSTRVqYQ9+4dvtnLsgQM/9+C23ECZnwf9F6WFWluOCbm9GrcSEiZs0Y0AF38Q6jqJjT/"
    "SRJPw2yuaFB33+yKOCj/wr5djx2gtBWz7sW/2luFmYB9kciQtoUO96f2Xpvu0cQDHkguikDYZb4L"
    "M2DOZ/Bsp+j0jyAkKge1Kyv9Bjx4MEv1zFstJwcLlSis2WcCI5aFgSwtNYiLhxqh5gcZIZvSRAXq"
    "8bPzHvcBvK696NIG0zGXBmOgdwbROLi49GbYFOYwZ2sKBtpy2gINo7jgwoFUAWRnWWeIjQl6FwSF"
    "1VnV6NxhnOkNTpaBKCIBR52dOzzUE+D5IAWPN7oV4HQUEBG1Vp5oKDkBSvT1Ipmgu4s0VVDyWZj5"
    "A3R5bnV7SsZhRJwnMABOhfzufJaATGAiCuSPElGY28PQkzKTpTCcBUTZgBJgsBLo3PI0sC1KhVUX"
    "ggbalnPOzISzTiZeNEKVLW3khVsdnCAoQ/uPIUqmIJgandGSnTsty/dEuPCPk1wcU80vRgoUgTwb"
    "DrbPEWP65sLaKhyhA4gyaQUeGx1F6F0LtexaJKyjJWrv9EXnS42AdoZJWZEdLgMxHTWZYcGH+A1K"
    "ms4bduexgQOQa/75j/9VMYWSJpxsh5xyEwpR2Lfc0d88KUHWwnia2BAkBXnLdoAhiu/WKG++Ntx+"
    "sRB3a9olXxt+u7mBD/Z0GrF88lTlXshI4dNni3rwQ37U1ypqK3lKzaISJ5/cYmYxYuFRGVJQNMzu"
    "b9k8uKmaq9xmZzvtYQB4TILCf7ZJnbpLPY28C/QGrdLFFN/siFpyiq2fEN8MBuIQQtpWutLqNc37"
    "XXC2htyxdn4GZD1n0kI070Pg9+0LHdDjk+Cm+YSQgIebW+rpHeLYoPCH+LiKbIdirck/NqePnTWl"
    "AYIqIelzRpnzyG4drIqsh9Sjyh+zTifqhRyOqTCbQ3B+kWNqP5J/rkMsUPXEHJtT43qA/rQWoaus"
    "PUxhhjFUgjtGibjIkmvEk635LAFtBhLQyEZ8NsEC/OA1bjDYdsimp6/5uZjj5g0rLwDjkMo8Y3V5"
    "LnZUKrRrXSzQKxuVfCwH+dmlZe5l6COD72NwlEPiEOIUcP6m/1fL9oi78OnmcGvhiorjF8Rydzz0"
    "msqEjtBfXuuvrTn82mrY1KlVJtSNgCZyFn2DDas3IDWLO8Rci4XaVNghb9d6RUyCfMecC1SFRQAL"
    "Bs4obrqASthU5rjmzob+Dbmzuc3wHAgEN3uGc7CBygFbfUMOfnuRDKOiXp5B8/Oa93t6mwbK/f3B"
    "iwr+bPq9oLZN1t6PwbENfTXHviik5nJTdmimWpwbKEC780bOJlF22QwFasnEUj5ukY/oL/CNIX7U"
    "4ObjiOMytIeUo9npNv+9ioXx+4PYmFm4ar6MjR9h+6pObSthgGmaSPZOSga37yqsOji8ngpEMdFG"
    "ddjgbmhUmtdhg7/R9+6ZEvIjhsJ6t/K//tNoziZjoTdD1PClQfu2Zs+aARag9+Pu8bv9d98NeRtM"
    "7eeJtCj3ivUOanJF+/2N3TrL6TVDaRVzAWxMaYVxQbtm197tX6xuaUE21Fhrh4tS0dJWPObQrlwz"
    "bVC+3KGlxCZ+1DHF3QhzALdGdoR3fC/DNAVx0nOoJ1+qBTxJimxiBGIOrJZiCnBZgScsM0tn5kVN"
    "x7ZfyYsfgT+tXX3V+RqpvlJAKJFSLS926JjrD2VtQKlUdWFAZfrw30WC4zWSOiWKVqt3faGht46N"
    "xRc7hIz+PuxIegBie8fHh8fDqkphHsq5BwxNS1GOBiw4SSgZ4IrXuMvOu/DAKEAWy1nJPbXhXjfx"
    "F4d/69CQt2orRWmXh2lGtPSkFFsbO0/A1E94TxtkACsFKpbTVR+qPENt3rll35l3hSrsbEpewZQi"
    "MemizwJDq9iDvIypGeIwUAy/GmKI4DqX4l1iYlVG7dOkiP36YmBmiqdhc7kGWM6HLIK2HHfsDQ0J"
    "l7MNEAEShWG1o0q2Yt0CBayaLAxSngIQcAHR0GnVU7p25aoirUhzIf9SYFtRtGbfa+HI8pRHIyPQ"
    "jlXLOHVnRyPdnbEt7ecDkuXKPdijP0DoxsJpp+BxFlcxwhKN2tId+1wVk4EjDYyIPTtYgjz95Rxx"
    "v0LXmDttTavVdGBYRd180R5Ev6qZW2VRUf/dtdZOTx3c0P/47473JW6NgMt+aRRk4X7YPMWNKpy+"
    "quyQQeqh695ZA+Zqn+DevPgD/J12ghyLQVzKklfaWyfKZTbpcwZdz83YKPJl/vA8OkD6xJl0GH75"
    "1tAfSLMv3y4yE/CKvq0EPHV95A6Omaxu2/FyJVca8ASJXMvgl/Z1p25f27audCMHrMpVReAQ03aH"
    "f+NaLnoBalKlHV0K8mBQDu8O9k8Odk9fff9F251LGotJO0Zz0MiVuKw0CKYjDKbSEGlwpUsaN127"
    "EnblUTfF/lOn4GtFolXWvVEc+jkS8MuiljceLE6Vij9WCUsk0IgrQTDTS8FgeDHLdXxAcCrDWNbg"
    "WF27ODCvVm6+qn6qbd10WKfmYvPQOyIFL2hkTgsi76i2jPT0zCL1Rslb7krsSOA4s9oFB9dBUYWe"
    "YQrnztOpl6HwaO4e2nnVmgWRG3M+nv0M7IG90cmy+bVTbj9Mw9i3v0QVHgXNHYgYgVPvunCAiGLC"
    "qCWqSp68KLJvsCu2Qzj0pT1Eg7yM2Vl8vsrO6nqtHWGp2iyrtU40Jes6jLe3UDfcPH+Gf1wwWWxi"
    "+D0MVqT0IrgJKn1lDMAVXwZ8eK2LvrD4yPKyOcP20J+Aj92BH4/nMzRsrbs1Uape+POLtivQhLNk"
    "YjctGE+4nL3XghXh4xWgvLmvgQVjq1kUwxxrLw0gyrzlK3RjW3nLmibSiqeK3h4isg8QRKXf6WnL"
    "GXxFFbrkBMJ8MZum0KHMcVu5CK/IE4jnQvBEo1qkpgB+B+iA8zj34gJbcBW+DgMYQZfn7YbJ+gqX"
    "kip+GvWLVW1bXysWVgbNXIyaxB0QgRM4ucdbOUZ68o4hGAmf0kqpN/h57bwr19OVKlCdxhmIJKxC"
    "ySS13EG3r07VGMMlyQU10S64mG3gcqyamgV23dP1ncz9nC0Q3oWHdcnEheA8gO9w8v7gRDFRWoxB"
    "P84CVajFuUfiyT7ptFjFsBCNyTJbXtfBbf1LPfUq1TYWq/Etx+nTupckwiGGy8O7/CavoqIl7IEg"
    "6tzR9HfqS6Bhdmjn+nIw4GWrocFoBMoF0YGsbMTVyo+sxdWNqi+NWUfRl7ZTEe4wY7y7pKgIyU72"
    "DzxCmUZhbnfXPAFtIirDgfbkkG5RWoa+n22euxFXelhfWvS2JoPdQxtzZCgb583VqDvIK/NWzOyK"
    "u7tSVm2fmZvWXWX2is3cVsP3XuEuN50kXBV4NuwsARLCfqUzGIQtJyMp5IVOpWZ5It7TOaTu40dq"
    "Cz8pcjQuq7je8tK00jS15TGTSWTkhr3VEqGGW5bnY4Src0P1rGPJwurwgPtLmL7RK0ic/LG95B9d"
    "FUOh/6SH70jZVoQwSt2xfgD8GOP0x7pAo41/snSOJ8bAvslBKLttBeckwhhWRsNvZzU0UroESeYL"
    "a0kZHdrTUZnioBMIZfIJYhv5u1KAlnNuYhVKsz3hdHZuorOsrAHFkAYgTBrOOJ8Iazg3eLpoZ8mk"
    "2BNJ00dwJ67UTmf+iOekoDXc8SxJQPzJw+rzITNFOirJaffR/YjC1L7NdOzKTztdea0Sk+ua6WL/"
    "RR+hIA1pYxtjrcijpiNL9eeAo9oNcJZkE2+CJgl51lPnEcW4yDrkwZsupkWYGu49+cTWH8ODquOD"
    "VXmge0KKal15WUfL1nU5kzADdx58qB2WwAE6s79+Wf9XXyq1uPq0DMHo3v5oKv5DsNw13QiWgBae"
    "EyOl4m/+q05ruUdk/c8s/GP1u5bCd85XlS5b+3F5qmGNToWyN44EXqPUaKo3MVC3gMsC7t4kF7fg"
    "3IrypCh1dJegq9QMpsh6XdxQX/sufoNpTWbzxLehX19sJF9/9ZXTyhi/bZxRXU3PNg0B9nkrUvk8"
    "1GlSRA2mUzZpSqaWTx2DQboNuH4vK3i3SLWrtmbYx6BcfL+erQauxtlRN2OjR0GozCDOCv0eQz5M"
    "E0HJp0+eZHuNB21mIDx0nhZniNYNPvebx4n7KJ8QUeLLz5BzC+XI8+cgMkpg67Ug96RT2PDRIchJ"
    "fpuquszGUvMbF7SaH0UuBFBRtL3l7ks8c7Ib7/LguHm60WSShE6EBEXoswe68bAsnFoxMtV4jovS"
    "tN44wtSDvJR2K5PoUTvMIfrhJJdDEfqqor9PdV19AQKIX0pIVU0vQuR63Xuo1yncVOtryCOwud1S"
    "JGdWJMfRJbrmgwGdy8RPCf6PZ3T6R7un3/dP9n/Z65/+fLTXPz7onx7vvusfHL7eewv/v393enS4"
    "/+4Uwqz2wRcvzTEnA4ikBZeHQIwGDoz+qE70bG9g1asPH7sth3FgCto4HOeOo2Ry6QdXIUyNo90l"
    "xoVaI5dw1GRR/Ua3/SB668rlu6URlRX61lD4ZxaaBIovKdAc6sGM3aT+ciC06tDJVr34OxfFc42J"
    "ruxfAaTkGQA0TpJIA8sgLCNQ+gE4jbriHv5Q+rCQY1zl+XxiOSvxLGJwNxsD0NMUrGGOCYTO3gsj"
    "bIvu8UNIwLzrNr+eES3w6LBFZ3Gp1NsapPoTcFOQxR69TWe3ElNjXbwoHsacqzmSRqUDt3zmW5/i"
    "866dNucGV0hmasok240iVMxyN/aPwJ0N6WqGpawbT5PRAyiC7WoUgXEfMv0/RAeNYJsUGu2OI2j3"
    "yxbLlbUOU6BqBfhbyRZCZjqe4ubhyX0yVspX1fEg8EPvHcbjhpQt6d0SrArMsX5F8A6zPcWCr0kZ"
    "LRWHpiAZeK2WpRVy1G00U7QZlAwekCfw7+KEvKfB4fhXdKLeUbFm/00WwlpEt0iRPtKz/7KQWDrZ"
    "tzomYO3LEzqa3t+XL8EBBqivkvgqyPLTZPBXtBvO/dYHVCb672SmiWvfJUdZQkdW8durZD4HrwU+"
    "p/L3y3DbwDzvZmPMIgKODfPSOq4iyZuLJ4GNHfpkxru2kRjaGf49b6mDjJK08Gr4+yVjan2Af+6H"
    "D0dK0b3OwqvgLjtb4xXFRPcS3lP1uUORnVnceJmS1PKWMW8+XM5UB5OrHilntgKh2LA0V24BtMG8"
    "IJmt9ycvkVlOXuP/Bwevlhkvi29S0OKmYGsuZuDlQ+Toh0gu8dUyCb03OakjqmrfhwwKu3m1vR0s"
    "gMUMZaOYjloam7b43U6LLE1ksGPRLSk6tah9x24n1dwOoUetvSksYCMQVJ/kiv0YPOpcHU0wbgew"
    "6b6gjM5Yc8COBVm017GqZqkq/SWbSEFKGfJp2Cg4d2p6i6FVq+b369X8hKshlbl3YXjOdWew4rmG"
    "GGMnLYhmqw4YirlWAVB6mmaWJTkdTbecJSX+WODvn62FPm6GmWUx1UaYoBYkbtxoTaxxQgKHdboL"
    "9ckAKOnvqMf3sT4bSXfWqMl/QEF9H3jCD25axfVdNfX3lK8tJaoCdjrzcqyr8YS62IqukqDQPZhy"
    "tT6yhfSmQX57z1jE8isYQQ1pVGx7LCMQ5weSuuOdNBnutMogmtJlBFXotrxSezcLMH8hvLFMoiIP"
    "QMpxy5oOWkqT7++t4NbaQOW6UexHFNhXkfa9GWOFHbTrEv3GzVYdNYoo6aoVXzp3wnmSNvUbeUhS"
    "4m/1zr+KBFhzEEKNlIGBF6V7cK2xlgOYAZuBdgP5R1WOxTkSr7QYcDpH3VNG+yCy8JNhp+zhG3EH"
    "XIVJ40mR4yIuqqrF1o1BC6G07OpJms7Zp5sa/h1MIq0mcXroLrWSa2vHBRmfGpi1PnaK1QETrp6m"
    "xJvKci1R2T2tJiqDw4YGsK1vq/vDTprML/S5kY7ysxKAX1Yp0QGD8ts3JYAOM4o2Ik8SIfFWomFV"
    "flepT90ZjzmRDNfeGsq1o5jiZ5DVmM4Gg50OPDDUtWN2duv+G2cJ9Spbt0tXwOWJ2DvePdkzNL7d"
    "iRRLBWXqhq0qCMq8mh2ruep8LGY9fGUJphYqcc5XEiFQfEF4Iyr/nugzJHaJk2McciE4X+zguoAn"
    "et7WGHju1w+ZzasDBxP0mqMo8Pv4gvi7vGDmEQJkVv6fepfGJJLplDbfZSL0HZoRlqpdJHw6W4or"
    "ULXzQLpd+enHRCRLg5GpdaLjrAF71rSssfbIxWBfHio0/yUH93FFduIR8YyZi/4RaAq0xbw8KDM2"
    "UFg7SnRCXnW7TH+O1/nRrS68qEsyi0pBs2dHXWq7cRSsc7qq6Qop8Nwkw4Cen51hkYOK8p3hOa4q"
    "Jjo4lwcd5gWwzxTkLcg6ruGh3YCO0muGja+eYlprXEynAZDnYmejXYbdedPPQ6/xKWu0dYH2J7/M"
    "Z2XN9gOv8zGrsEldt2qwtbr4nRfpIJL0rrFr26oXUvtMU3kbT2zqBTSOE9up91t9OKN2QKN+KJls"
    "GJ4WwHNMrtijFIfmfH2hJAkE3+VaHkTjAY+CbB7SMQNyZIftEaoWwKNxqM616T0jMsJNi71euR2N"
    "4Q5PaJiloeGHGKUZTLMHVNKFKjryCWOMDR+3g/Kp9d2jdd4UN0zuSck+RvGxz0u7ViNcYu1NNX2U"
    "cl/rIV5KxU6ty3OHjYvs8BJmuk6X79ybJzIn9oPQHXzHP1fXAGBEMk6SfF1dfEkMKZvQtly+lZeh"
    "YR9qxgdB+T49qofFbXl6hjfMNoHg3cc/nT4TDISca/MaYJufzABVSfei8Onz1v5Rr35HlmDINoEO"
    "uafwroAz0UvGs7AGXO0uTOWo86h4hQ4y2mbZmk6wbWLel4iKL7fw295P8N1aUKBWwixX0hgFsN++"
    "t7iCxrFwIpbJDFP56Li1zi5lIn8Vt5wAEwK9pkUUDUgppWUvW3OL08EXP4ZpwEQnZwp80Ezd1Ke7"
    "U7jSR+/0Suu7yIv18WRs170YaQNtc0loaxITyNThB/Kf+CG2Ar/1aF9l5tTns+Hm5rnO0T3U4cX1"
    "AtUJ2gyMj1z0dRRyZyC9UPuk+h6vuiCXcbU+//yXjij+lfZAlyzkI7dU8RAbZpUs1Ox8oqIe2NXK"
    "wJaoYALyFIDg1d1TSXrXw50b9sPO+1ysyAdTKt23ubXRyk3XVniHJGdZMeZRnWmYnep06aCPWdIk"
    "aQiW0vYwyyY5v5xK92rq8b7dG/yfpXyAXKf2wcup35fzZ8o0jUKDMLRLotBlNfJIdIMbje9nxLHr"
    "DsJ7sMqfVUQcvP0cqD1oo/aBjLdy3/JjkCWvaV9AWHKWZHmHANxDwpqY0+X36YP5GfxdUTJzi7uV"
    "9dtDu2z1HjynIIP1UpOCAcrlsQ5eHvOF/dYD1+rR67Skema6NO/UzD+V3tKKDJRKuA5Wub4PpD/f"
    "Db/8hmwkK/KYm9/kDYjoVXL9rqWKwigVUHNAcTVQwcXW+SrO/WIJ5/IQT1HRTyBCy02DCQSb43Xg"
    "q9ZvqrxP4KodsG66aHGhLvJU5kz8VoC7SieyILq4aOJahbxMLDxTbC09hqACRjC5FtOS5kB3rn5o"
    "bs12MjFd7QtjrKNB4hEfIog1/vkDYZiB0yusnPOP+NvqaEkNy8GSsIObMKeIyWWWwzuVF44rDpWn"
    "2mfHfZ0dbrxyBS/CAPcGq/TaCUDEfs1P5FRS0zVyWtbIOODZc3iAdYR0MWBIJ0Rv6Q5AChaNC094"
    "ghhYvEvyN5hJXz2pA+5P+HEAyCGzNw8WtA9HP38R5u3Ntk9dR/he/9jGZygNLH/Io3XN2Hvzx0A4"
    "kyX1FgOlePvlGVz6EQlO9K/x5RTSbSRKT9XFOvwDIkBPfbX/MnfymHNnSGOjsJMDMLt1ZbkDna9/"
    "j+fZqqdWys+AxD8l4WbzPAuCSjmCqgBZGgXIRLJ1QL688btEmknYvIjuNMF8QoiJIZ+vgDGvIVI/"
    "t8I7XH3aKldKv1y3Ojil0DF+pRpdHXmWzUfXbKLcMQjsegVmNPcmWIasEg81oGYzOivqypnDG3IT"
    "zDiXR+Vg/T8H/x8EcQEr/ert/icWgIO9d+/pTkSr/qNOrcv0qhPyEtR7vzx0NaC7oEO8qpZCxb36"
    "Tpz6iSN9GQ7WU3MZdWf/bQOBp6o6etlBfX0y3Pi1o9qW/bVxhZZ9UYQ+D/HV0rYdv3EEoad/heJD"
    "XZ/rXztSP3aEuzBl8QEnYtZVCmWdsyAqFMfOX0P0PUuujfsVZfnTM+YNW9D0hVvpO/zhINIC9Tt8"
    "SqGH5huu+LcizPnHZFChzYFZOi8mbZ9M7kozM8sjY1TqYtmde1XQvmEol1bmNZwKw0Xf7HB09O05"
    "5qV1nXlsboiUK/WkZjnQFk0VWM/r1i996gjV7okjDAirO29bK46P6gNVKyE863IG6weyVvb/qqN/"
    "Y3t+Zf/nVucJ0yrVubL318uif31r7sreLzp6G0Z6Zd+N5XmHl7fBA2OC7pBYgXmvfsSFWd9tHwlt"
    "3XPeeXLyQ1y+r1vmRx0s5Z2CMjfP4g8+mO1lF1dKDiZzn3KbJYDysjdrCDw1H/vesC53VUShb7Mx"
    "WppCYDbks1EdEDW/Go2JEwetLg0Gb3bAwkOThc33HNQOTR41XhPXwVuDB423lSMxrPiM3y96xnFo"
    "oqn4VmxyzhC+nW2eYxUJUnhoXIfW1LJ6Fc5Un3Otj6Mm5LYPrtlNuSVi7U4BWay5Qm2SSOAA/D0m"
    "jrdwJHW3AV5dkiCmBf6emrrGISAD0VGbtNVxxpZtiVnrs9HrAdYjukZhNCKhG42Q50YjJXtcwxLm"
    "NnEifqP5Ob3/A72zTZM="
)

SD_NOTE = ("SD / microSD card required for flashing: 8 GB minimum, "
           "16 GB recommended (the app shows the exact size for the "
           "image you pick).")


def detect_os():
    s = platform.system().lower()
    if s.startswith("win"):
        return "windows"
    if s == "darwin":
        return "macos"
    return "linux"


def os_label(os_id):
    return {"windows": "Windows", "macos": "macOS", "linux": "Linux"}[os_id]


def app_source():
    return zlib.decompress(base64.b64decode(PAYLOAD_B64)).decode("utf-8")


def locations(os_id):
    home = Path.home()
    if os_id == "windows":
        root = Path(os.environ.get("LOCALAPPDATA",
                                   home / "AppData" / "Local"))
        base = root / "RaspIOSex-Me-Baby"
    elif os_id == "macos":
        base = home / "Applications" / "RaspIOSex-Me-Baby"
    else:
        base = home / ".local" / "share" / "raspiosex-me-baby"
    return home, base


def write_app(base):
    (base / "library").mkdir(parents=True, exist_ok=True)
    app = base / APP_FILE
    app.write_text(app_source(), encoding="utf-8")
    return app


def make_executable(path):
    try:
        mode = os.stat(path).st_mode
        os.chmod(path, mode | 0o111)
    except OSError:
        pass


# ---------------------------------------------------------------- Windows
def install_windows(home, base):
    app = write_app(base)
    pycmd = "py -3" if shutil.which("py") else "python"
    run_bat = base / "run.bat"
    run_bat.write_text("@echo off\n" + pycmd + ' "%~dp0' + APP_FILE + '" %*\n',
                       encoding="utf-8")
    desktop_link = home / "Desktop" / "RaspIOSex Me Baby.lnk"
    startmenu = (Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
                 / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    startmenu.mkdir(parents=True, exist_ok=True)
    start_link = startmenu / "RaspIOSex Me Baby.lnk"
    linked = False
    for link in (desktop_link, start_link):
        try:
            ps = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut('"
                  + str(link) + "');$s.TargetPath='" + str(run_bat)
                  + "';$s.WorkingDirectory='" + str(base) + "';$s.Save()")
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy",
                            "Bypass", "-Command", ps],
                           check=True, capture_output=True, timeout=60)
            linked = True
        except Exception:
            pass
    if not linked:
        (home / "Desktop" / "RaspIOSex Me Baby.bat").write_text(
            '@echo off\ncall "' + str(run_bat) + '"\npause\n',
            encoding="utf-8")
    uninstall_bat = base / "uninstall.bat"
    uninstall_bat.write_text(
        "@echo off\n"
        "cd /d %TEMP%\n"
        'del "%USERPROFILE%\\Desktop\\RaspIOSex Me Baby.lnk" 2>nul\n'
        'del "%USERPROFILE%\\Desktop\\RaspIOSex Me Baby.bat" 2>nul\n'
        'del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\'
        'RaspIOSex Me Baby.lnk" 2>nul\n'
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        'Uninstall\\RaspIOSexMeBaby" /f 2>nul\n'
        'rmdir /s /q "%LOCALAPPDATA%\\RaspIOSex-Me-Baby"\n'
        "echo RaspIOSex Me Baby removed.\n"
        "pause\n",
        encoding="utf-8")
    try:
        import winreg
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"
            "RaspIOSexMeBaby")
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ,
                          APP_NAME + " " + APP_VERSION)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ,
                          str(base))
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ,
                          '"' + str(uninstall_bat) + '"')
        winreg.CloseKey(key)
    except Exception:
        pass
    return ('Double-click "RaspIOSex Me Baby" on the Desktop or in the '
            "Start Menu.")


# ------------------------------------------------------------------ macOS
def install_macos(home, base):
    app = write_app(base)
    make_executable(app)
    launcher = base / "RaspIOSex Me Baby.command"
    launcher.write_text(
        "#!/bin/sh\n"
        'python3 "' + str(app) + '"\n'
        "echo\n"
        "echo 'Press any key to close.'\n"
        "read -n 1 -s\n",
        encoding="utf-8")
    make_executable(launcher)
    desk = home / "Desktop" / "RaspIOSex Me Baby.command"
    try:
        shutil.copyfile(launcher, desk)
        make_executable(desk)
    except OSError:
        pass
    uninstaller = base / "Uninstall RaspIOSex Me Baby.command"
    uninstaller.write_text(
        "#!/bin/sh\n"
        "cd /tmp\n"
        'rm -f "$HOME/Desktop/RaspIOSex Me Baby.command"\n'
        'rm -rf "$HOME/Applications/RaspIOSex-Me-Baby"\n'
        "echo 'RaspIOSex Me Baby removed.'\n",
        encoding="utf-8")
    make_executable(uninstaller)
    return 'Double-click "RaspIOSex Me Baby" on the Desktop.'


# ------------------------------------------------------------------ Linux
def install_linux(home, base):
    app = write_app(base)
    make_executable(app)
    bin_dir = home / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link = bin_dir / "raspiosex-me-baby"
    try:
        if link.exists() or link.is_symlink():
            link.unlink()
        os.symlink(app, link)
    except OSError:
        link.write_text('#!/bin/sh\nexec python3 "' + str(app) + '" "$@"\n',
                        encoding="utf-8")
        make_executable(link)
    apps_dir = home / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    (apps_dir / "raspiosex-me-baby.desktop").write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=RaspIOSex Me Baby\n"
        "Comment=Download and flash Raspberry Pi OS with balenaEtcher\n"
        "Exec=" + str(app) + "\n"
        "Terminal=true\n"
        "Categories=Utility;\n",
        encoding="utf-8")
    uninstaller = base / "uninstall.sh"
    uninstaller.write_text(
        "#!/bin/sh\n"
        "cd /tmp\n"
        'rm -f "$HOME/.local/bin/raspiosex-me-baby"\n'
        'rm -f "$HOME/.local/share/applications/raspiosex-me-baby.desktop"\n'
        'rm -rf "$HOME/.local/share/raspiosex-me-baby"\n'
        "echo 'RaspIOSex Me Baby removed.'\n",
        encoding="utf-8")
    make_executable(uninstaller)
    return "Run it from your applications menu, or type: raspiosex-me-baby"


# -------------------------------------------------------------- uninstall
def uninstall(os_id):
    home, base = locations(os_id)
    if os_id == "windows":
        for p in (home / "Desktop" / "RaspIOSex Me Baby.lnk",
                  home / "Desktop" / "RaspIOSex Me Baby.bat",
                  Path(os.environ.get("APPDATA",
                                      home / "AppData" / "Roaming"))
                  / "Microsoft" / "Windows" / "Start Menu" / "Programs"
                  / "RaspIOSex Me Baby.lnk"):
            try:
                p.unlink()
            except OSError:
                pass
        try:
            import winreg
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"
                "RaspIOSexMeBaby")
        except Exception:
            pass
    elif os_id == "macos":
        try:
            (home / "Desktop" / "RaspIOSex Me Baby.command").unlink()
        except OSError:
            pass
    else:
        for p in (home / ".local" / "bin" / "raspiosex-me-baby",
                  home / ".local" / "share" / "applications"
                  / "raspiosex-me-baby.desktop"):
            try:
                p.unlink()
            except OSError:
                pass
    shutil.rmtree(base, ignore_errors=True)
    print(APP_NAME + " removed from " + str(base))


def main():
    if sys.version_info < (3, 9):
        print("Python 3.9 or newer is required.")
        return 1
    os_id = detect_os()
    if "--uninstall" in sys.argv:
        uninstall(os_id)
        return 0
    home, base = locations(os_id)
    print("=" * 64)
    print(APP_NAME + " " + APP_VERSION + " - universal installer")
    print("Detected operating system: " + os_label(os_id)
          + " - installing the " + os_label(os_id) + " version.")
    print("Install folder: " + str(base))
    print("=" * 64)
    if os_id == "windows":
        how = install_windows(home, base)
    elif os_id == "macos":
        how = install_macos(home, base)
    else:
        how = install_linux(home, base)
    try:
        shutil.copyfile(Path(__file__).resolve(),
                        base / "RaspIOSex-Me-Baby-Setup.py")
    except OSError:
        pass
    print()
    print("Installed. " + how)
    print(SD_NOTE)
    print("Uninstall any time with the uninstaller in the install "
          "folder, or run this Setup again with --uninstall.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
