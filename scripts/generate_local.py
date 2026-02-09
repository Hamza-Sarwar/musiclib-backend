"""
Local AI Music Generator using Meta's MusicGen (no API needed).
Runs on CPU - each 60s track takes ~30 minutes.

Usage:
    python scripts/generate_local.py --count 10
    python scripts/generate_local.py --resume --import
    python scripts/generate_local.py --import-only
"""

import os
import sys
import json
import argparse

TRACK_PROMPTS = [
    # ═══════════════════════════════════════════════════════════════
    # ARIA VALE — dreamy female indie pop / acoustic (English)
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "dreamy indie pop, soft female vocal style, reverb guitar, gentle piano, romantic atmosphere, warm production",
        "title": "Paper Moon",
        "genre": "pop",
        "mood": "romantic",
        "bpm": 95,
        "artist_name": "Aria Vale",
        "language": "English",
        "lyrics": "Hanging wishes on a paper moon\nHoping that you'd find me soon\nSoft guitar beneath the silver light\nDreaming of you every night\n\nFold me into constellations\nWhispered words and sweet sensations\nPaper moon above the sea\nShining down on you and me"
    },
    {
        "prompt": "sad indie pop, melancholic piano, soft acoustic guitar, heartbreak ballad, gentle female vocal feel",
        "title": "Glass Houses",
        "genre": "pop",
        "mood": "sad",
        "bpm": 78,
        "artist_name": "Aria Vale",
        "language": "English",
        "lyrics": "We built our love in glass houses\nEvery crack let the cold wind in\nFragile walls and silent promises\nShattered by the noise within\n\nI can see right through the pieces\nMemories scattered on the floor\nGlass houses don't keep secrets\nNow there's nothing worth breaking anymore"
    },
    {
        "prompt": "gentle acoustic fingerpicking, warm morning atmosphere, soft folk inspired, peaceful female singer vibe",
        "title": "Morning Gold",
        "genre": "acoustic",
        "mood": "peaceful",
        "bpm": 88,
        "artist_name": "Aria Vale",
        "language": "English",
        "lyrics": "Morning gold pours through the curtain\nCoffee steam and birdsong certain\nBarefoot steps on wooden floors\nPeaceful mornings, nothing more\n\nGentle world still half asleep\nPromises I want to keep\nMorning gold upon my face\nA quiet, warm, and tender place"
    },
    {
        "prompt": "sad acoustic ballad, broken heart, fingerstyle guitar, emotional depth, intimate and vulnerable female vocal style",
        "title": "Broken Compass",
        "genre": "acoustic",
        "mood": "sad",
        "bpm": 75,
        "artist_name": "Aria Vale",
        "language": "English",
        "lyrics": "My compass broke the day you left\nEvery direction feels like theft\nFingers tracing roads we knew\nAll of them still lead to you\n\nNorth star faded from my sky\nToo tired to wonder why\nBroken compass in my hand\nLost in love I can't understand"
    },
    {
        "prompt": "sad rnb, soft piano, slow tempo, emotional female vocal style, heartbreak, beautiful melancholy",
        "title": "Empty Room",
        "genre": "rnb",
        "mood": "sad",
        "bpm": 65,
        "artist_name": "Aria Vale",
        "language": "English",
        "lyrics": "This empty room still holds your name\nEchoes playing the same old game\nSoft piano where you used to sit\nI keep the lights low, candles lit\n\nYour shadow dances on the wall\nI hear your voice down the hall\nEmpty room but heart still full\nBeautiful sadness, bittersweet pull"
    },
    {
        "prompt": "melancholic rnb, ghostly reverb, slow beat, haunting atmosphere, emotional female vocal style",
        "title": "Ghost of You",
        "genre": "rnb",
        "mood": "sad",
        "bpm": 70,
        "artist_name": "Aria Vale",
        "language": "English",
        "lyrics": "The ghost of you still lingers here\nIn every song I cannot hear\nHaunting reverb fills the space\nWhere I once memorized your face\n\nYou left but never really gone\nYour melody keeps playing on\nGhost of you in morning dew\nI'm still haunted by the truth"
    },

    # ═══════════════════════════════════════════════════════════════
    # SHADOW — dark male electronic / hip-hop (English)
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "dark trap beat, heavy 808 bass, atmospheric pads, aggressive hi-hats, dark male vocal energy, urban night",
        "title": "Concrete Shadows",
        "genre": "hip-hop",
        "mood": "dark",
        "bpm": 140,
        "artist_name": "Shadow",
        "language": "English",
        "lyrics": "Moving through concrete shadows at night\nCity breathing under neon light\n808 bass shaking the ground below\nEvery step part of the show\n\nShadows stretch across the wall\nRising up before we fall\nConcrete jungle, midnight call\nShadow rules above it all"
    },
    {
        "prompt": "cyberpunk electronic, digital glitches, deep bass, mysterious synths, dark futuristic atmosphere",
        "title": "Binary Code",
        "genre": "electronic",
        "mood": "mysterious",
        "bpm": 128,
        "artist_name": "Shadow",
        "language": "English",
        "lyrics": "Written in binary code\nZeros and ones down this road\nDigital glitches in my mind\nLeaving the real world behind\n\nCyberpunk dreams flicker bright\nCircuit boards in the midnight\nBinary code running deep\nSecrets that the machines keep"
    },
    {
        "prompt": "dark ambient electronic, low frequency bass, minimal techno, eerie pads, late night warehouse atmosphere",
        "title": "Night Frequency",
        "genre": "electronic",
        "mood": "dark",
        "bpm": 90,
        "artist_name": "Shadow",
        "language": "English",
        "lyrics": "Tune into the night frequency\nDark waves pulsing endlessly\nLow bass humming through the floor\nWarehouse echoes wanting more\n\nMinimal beats in empty space\nShadows dancing, no known face\nNight frequency, cold and raw\nDarkness without any flaw"
    },

    # ═══════════════════════════════════════════════════════════════
    # LUNA RAY — dreamy female ambient / chillwave (English)
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "ethereal ambient, soft crystal pads, gentle wind chimes, space atmosphere, peaceful meditation, dreamy female energy",
        "title": "Stardust Lullaby",
        "genre": "ambient",
        "mood": "peaceful",
        "bpm": 55,
        "artist_name": "Luna Ray",
        "language": "English",
        "lyrics": "Close your eyes and drift away\nStardust falling where you lay\nCrystal pads like gentle rain\nWashing over every pain\n\nFloat among the distant stars\nHealing all your hidden scars\nStardust lullaby tonight\nEverything will be alright"
    },
    {
        "prompt": "chillwave, warm retro synths, hazy pads, sunset beach vibes, dreamy vocal chops, nostalgic atmosphere",
        "title": "Dreamcatcher",
        "genre": "chillwave",
        "mood": "relaxing",
        "bpm": 86,
        "artist_name": "Luna Ray",
        "language": "English",
        "lyrics": "Catch my dreams before they fade\nRetro synths and plans we made\nHazy sunset on the shore\nWarm nostalgia evermore\n\nDreamcatcher spinning slow\nCatching every golden glow\nChillwave memories replay\nBeautiful dreams here to stay"
    },
    {
        "prompt": "sad chillwave, melancholic synths, slow dreamy beat, reverb, lonely night drive, emotional atmosphere",
        "title": "Violet Hour",
        "genre": "chillwave",
        "mood": "sad",
        "bpm": 76,
        "artist_name": "Luna Ray",
        "language": "English",
        "lyrics": "The violet hour between the day and dark\nMelancholic synths leave their mark\nDriving alone on empty streets\nWhere the night and sadness meets\n\nReverb echoes of your voice\nLeaving wasn't really a choice\nViolet hour, purple tears\nDreamy sadness through the years"
    },

    # ═══════════════════════════════════════════════════════════════
    # KAI STORM — energetic male rock / electronic (English)
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "powerful rock, driving electric guitar riffs, heavy drums, energetic, stadium anthem, male energy",
        "title": "Electric Horizon",
        "genre": "rock",
        "mood": "energetic",
        "bpm": 135,
        "artist_name": "Kai Storm",
        "language": "English",
        "lyrics": "Chasing the electric horizon\nGuitar riffs like bolts of lightning\nDrums pounding in my chest\nNever stopping, never rest\n\nHands raised to the stadium sky\nThunder rolling, spirits high\nElectric horizon, burning bright\nRock and roll all through the night"
    },
    {
        "prompt": "dramatic rock, powerful guitar, orchestral elements, cinematic build, epic male vocal energy",
        "title": "Wildfire",
        "genre": "rock",
        "mood": "dramatic",
        "bpm": 130,
        "artist_name": "Kai Storm",
        "language": "English",
        "lyrics": "Wildfire spreading through my veins\nBreaking free from all these chains\nPowerful chords shake the earth\nDestruction leading to rebirth\n\nFlames rising to the sky\nBurning bridges, saying goodbye\nWildfire out of control\nA storm that takes the soul"
    },
    {
        "prompt": "sad rock ballad, emotional guitar solo, slow build, heartfelt acoustic to electric, male vocal style",
        "title": "Last Train Home",
        "genre": "rock",
        "mood": "sad",
        "bpm": 80,
        "artist_name": "Kai Storm",
        "language": "English",
        "lyrics": "Standing on the empty platform\nLast train home, the night is warm\nGuitar echoes through the station\nLonely heart and lost direction\n\nEvery mile away from you\nEvery song a shade of blue\nLast train home, too late to call\nSaddest journey of them all"
    },
    {
        "prompt": "dark alternative rock, moody guitar, minor key, brooding atmosphere, midnight energy",
        "title": "Midnight Rebel",
        "genre": "rock",
        "mood": "dark",
        "bpm": 110,
        "artist_name": "Kai Storm",
        "language": "English",
        "lyrics": "Midnight rebel with a cause unknown\nDark guitar riffs cut to the bone\nMoody streets and broken signs\nWalking on the edge of lines\n\nRebel heart won't be contained\nEvery scar a medal gained\nMidnight comes and shadows play\nRebels never fade away"
    },

    # ═══════════════════════════════════════════════════════════════
    # NOVA — futuristic electronic (English)
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "energetic electronic dance music, powerful synth lead, driving beat, festival energy, futuristic production",
        "title": "Quantum Leap",
        "genre": "electronic",
        "mood": "energetic",
        "bpm": 128,
        "artist_name": "Nova",
        "language": "English",
        "lyrics": "Take the quantum leap tonight\nSynth waves crashing, neon light\nDriving beats beneath our feet\nFuture rhythms, feel the heat\n\nLeap beyond what's known to be\nElectronic energy set free\nQuantum state of mind and sound\nDancing on uncharted ground"
    },
    {
        "prompt": "mysterious electronic, deep ambient pads, subtle glitches, futuristic atmosphere, evolving textures",
        "title": "Neural Dreams",
        "genre": "electronic",
        "mood": "mysterious",
        "bpm": 100,
        "artist_name": "Nova",
        "language": "English",
        "lyrics": "Neural dreams in circuits deep\nArtificial minds that never sleep\nGlitches forming patterns new\nFuturistic morning dew\n\nTextures shifting like the tide\nDigital consciousness inside\nNeural dreams expanding wide\nWhere the real and virtual collide"
    },
    {
        "prompt": "epic electronic, soaring synth melody, powerful build, euphoric drop, space atmosphere, cinematic",
        "title": "Starship",
        "genre": "electronic",
        "mood": "epic",
        "bpm": 138,
        "artist_name": "Nova",
        "language": "English",
        "lyrics": "Board the starship, leave the ground\nSoaring synths, a cosmic sound\nBuilding higher, touching stars\nFlying past Jupiter and Mars\n\nEuphoric drop like gravity\nPulling us through infinity\nStarship racing through the black\nNever looking, never back"
    },

    # ═══════════════════════════════════════════════════════════════
    # ELLA RIVERS — smooth jazz / soul (English)
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "smooth jazz, warm saxophone, soft piano, brushed drums, smoky bar atmosphere, late night soul",
        "title": "Smoky Blues",
        "genre": "jazz",
        "mood": "calm",
        "bpm": 85,
        "artist_name": "Ella Rivers",
        "language": "English",
        "lyrics": "Smoky blues in a dim-lit room\nSaxophone cutting through the gloom\nBrushed drums whisper on the snare\nJazz notes floating through the air\n\nPiano keys tell the story right\nSoulful melodies all night\nSmoky blues and candlelight\nEverything feels warm tonight"
    },
    {
        "prompt": "upbeat jazz swing, walking bass, bright trumpet, lively piano, big band energy, vintage feel",
        "title": "Swing Time",
        "genre": "jazz",
        "mood": "upbeat",
        "bpm": 140,
        "artist_name": "Ella Rivers",
        "language": "English",
        "lyrics": "Swing time baby, feel the beat\nWalking bass beneath your feet\nTrumpet blazing hot and loud\nJazz that moves the dancing crowd\n\nBig band swinging left and right\nVintage vibes on Saturday night\nSwing time rhythm, pure delight\nJazz alive and burning bright"
    },

    # ═══════════════════════════════════════════════════════════════
    # VICTOR CRANE — cinematic / classical (English)
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "sad classical piano, emotional solo, melancholic melody, autumn atmosphere, gentle sorrow, beautiful sadness",
        "title": "Autumn Waltz",
        "genre": "classical",
        "mood": "sad",
        "bpm": 72,
        "artist_name": "Victor Crane",
        "language": "English",
        "lyrics": "Autumn leaves waltz to the ground\nPiano notes the only sound\nMelancholic melody plays\nFor all the golden fading days\n\nGentle sorrow in each key\nBeautiful sadness flowing free\nAutumn waltz for you and me\nA dance with memory"
    },
    {
        "prompt": "sad cinematic orchestral, emotional strings, solo cello, gentle piano, film score, beautiful grief",
        "title": "Fading Light",
        "genre": "cinematic",
        "mood": "sad",
        "bpm": 68,
        "artist_name": "Victor Crane",
        "language": "English",
        "lyrics": "The fading light behind the hills\nA cello crying, time stands still\nStrings that carry all the weight\nOf words we whispered far too late\n\nBeautiful grief in every note\nA cinematic love we wrote\nFading light at close of day\nWatching everything drift away"
    },
    {
        "prompt": "epic cinematic orchestral, powerful brass, soaring strings, dramatic percussion, heroic triumph",
        "title": "Rise Again",
        "genre": "cinematic",
        "mood": "epic",
        "bpm": 130,
        "artist_name": "Victor Crane",
        "language": "English",
        "lyrics": "When the world has knocked you down\nPick yourself up off the ground\nBrass and strings begin to swell\nEvery hero has a tale to tell\n\nRise again through fire and rain\nTurn your suffering into gain\nDramatic drums beat in your chest\nRise again and be your best"
    },

    # ═══════════════════════════════════════════════════════════════
    # VEER KAPOOR — Hindi male, Bollywood / romantic / sad
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "romantic bollywood style, warm piano, soft strings, sitar accent, emotional Indian male vocal style, love song",
        "title": "Dil Ki Baat",
        "genre": "pop",
        "mood": "romantic",
        "bpm": 90,
        "artist_name": "Veer Kapoor",
        "language": "Hindi",
        "lyrics": "Dil ki baat sunata hoon\nTere pyaar mein kho jaata hoon\nSoft piano aur taron ki raat\nTere bina adhuri hai baat\n\nAnkhon mein tera chehra hai\nDil mein tera basera hai\nDil ki baat ye sun le tu\nMain tujhse pyaar karta hoon"
    },
    {
        "prompt": "inspiring bollywood, uplifting strings, tabla rhythm, hopeful piano, Indian film soundtrack, motivational",
        "title": "Sapno Ka Safar",
        "genre": "pop",
        "mood": "inspiring",
        "bpm": 100,
        "artist_name": "Veer Kapoor",
        "language": "Hindi",
        "lyrics": "Sapno ka safar hai ye zindagi\nHar mod pe nayi roshni\nTabla ki taaal pe chalna hai\nApne sapno ko paana hai\n\nHousla rakho dil mein yaaro\nAndheron se mat haaro\nSapno ka safar lambi raah\nManzil milegi, bas rakh vishwas"
    },
    {
        "prompt": "sad Hindi ballad, melancholic piano, gentle strings, heartbreak, lonely night, emotional depth, Indian male vocal style",
        "title": "Tanha Raatein",
        "genre": "pop",
        "mood": "sad",
        "bpm": 72,
        "artist_name": "Veer Kapoor",
        "language": "Hindi",
        "lyrics": "Tanha raatein guzar rahi hain\nYaadein teri sataa rahi hain\nPiano ke sur mein dard hai\nHar dhun mein teri yaad hai\n\nKhali kamra, bujhi sham\nTere bina adhura kaam\nTanha raatein, geeli aankhein\nToot gaye sapne, reh gayi baatein"
    },
    {
        "prompt": "very sad Indian ballad, heartbreaking melody, slow sitar, gentle tabla, deep sorrow, emotional devastation",
        "title": "Tere Bina",
        "genre": "pop",
        "mood": "sad",
        "bpm": 72,
        "artist_name": "Veer Kapoor",
        "language": "Hindi",
        "lyrics": "Tere bina ye dil rota hai\nHar lamha ab kuch khota hai\nSitar ke taar se dard bahe\nAansoo ki nadi, khamoshi sahe\n\nBikhre sapne, tooti umeed\nTere bina hai zindagi mureed\nHar gali mein teri parchai\nTere bina adhoori is duniya ki sachai"
    },

    # ═══════════════════════════════════════════════════════════════
    # MEERA SHARMA — Hindi female, romantic / devotional / sad
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "romantic Indian music, gentle sitar melody, soft tabla, warm flute, beautiful love theme, female vocal style",
        "title": "Prem Geet",
        "genre": "world",
        "mood": "romantic",
        "bpm": 85,
        "artist_name": "Meera Sharma",
        "language": "Hindi",
        "lyrics": "Prem geet gaati hoon main\nDil ki baatein sunati hoon main\nSitar ki dhun mein pyaar hai\nHar sur mein tera intezaar hai\n\nBansuri ki meethi taan\nPyaar ki gehri pehchaan\nPrem geet ye dil se\nTere naam ki hai ye kahani"
    },
    {
        "prompt": "peaceful Indian classical, meditation sitar, gentle tanpura drone, spiritual atmosphere, devotional, serene",
        "title": "Shanti Mantra",
        "genre": "world",
        "mood": "peaceful",
        "bpm": 55,
        "artist_name": "Meera Sharma",
        "language": "Hindi",
        "lyrics": "Om shanti shanti shanti\nMann ki ho rahi bharti\nTanpura ki gunj mein\nMilti hai sacchi shanti\n\nDhyan ki gehrai mein utar\nAntar mann ka suno swar\nShanti mantra gaaye ja\nDil ko sukoon paaye ja"
    },
    {
        "prompt": "sad Indian farewell song, emotional sitar, gentle strings, heartfelt goodbye, beautiful melancholy, female vocal style",
        "title": "Alvida",
        "genre": "pop",
        "mood": "sad",
        "bpm": 70,
        "artist_name": "Meera Sharma",
        "language": "Hindi",
        "lyrics": "Alvida kehna pada mujhe\nDil tod ke jaana pada mujhe\nSitar rota hai mere saath\nChhod rahi hoon tera haath\n\nAansoo mein beh gaye sapne\nToot gaye saare apne\nAlvida ki ye daastaan\nDard bhari hai, bejubaan"
    },
    {
        "prompt": "deeply sad Indian music, crying sitar, slow tabla, sorrowful strings, deep pain, loss and grief",
        "title": "Dard",
        "genre": "world",
        "mood": "sad",
        "bpm": 65,
        "artist_name": "Meera Sharma",
        "language": "Hindi",
        "lyrics": "Dard itna gehra hai\nHar pal ab akehra hai\nSitar ke taar toote se\nDil ke armaan roote se\n\nKhoya hai jo mil nahi sakta\nDard ye dil se nikl nahi sakta\nAankhein band karti hoon\nPhir bhi aansu bahaati hoon"
    },

    # ═══════════════════════════════════════════════════════════════
    # PRIYA SINGH — Hindi female, upbeat pop / Bollywood dance
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "energetic Bollywood dance, dhol beats, electronic elements, party music, modern Indian pop, female energy",
        "title": "Nachle",
        "genre": "pop",
        "mood": "energetic",
        "bpm": 128,
        "artist_name": "Priya Singh",
        "language": "Hindi",
        "lyrics": "Nachle nachle saari raat\nDhol baje aur ho barsaat\nPairo mein hai josh aaj\nDance floor pe karein raaj\n\nBaaje DJ, baaje gaana\nSabko hai bas nachna jaana\nNachle nachle ek aur baar\nAaj ki raat hai tyohaar"
    },
    {
        "prompt": "colorful Bollywood pop, bright melodies, festive atmosphere, happy Indian celebration, joyful energy",
        "title": "Rang De",
        "genre": "pop",
        "mood": "happy",
        "bpm": 115,
        "artist_name": "Priya Singh",
        "language": "Hindi",
        "lyrics": "Rang de rang de duniya ko\nHar rung mein rang do saari galiyon ko\nLaal peela hara neela\nZindagi ka rang rangeela\n\nKhushiyon ki baarish ho\nHar chehre pe muskaan ho\nRang de ye pal saare\nZindagi ke nazaare pyaare"
    },
    {
        "prompt": "upbeat Indian pop, cheerful melody, modern tabla and synth, youthful energy, carefree Bollywood",
        "title": "Patang",
        "genre": "pop",
        "mood": "upbeat",
        "bpm": 110,
        "artist_name": "Priya Singh",
        "language": "Hindi",
        "lyrics": "Patang udaao aasman mein\nSapne buno har pal mein\nHawa ke saath ud chalo\nZindagi ko gale lagao\n\nDor pakad ke rakhna yaad\nPatang udegi, hogi aazaad\nNeele aasman mein rang bharo\nPatang ke saath khud ko udao"
    },

    # ═══════════════════════════════════════════════════════════════
    # RAJ MALHOTRA — Hindi male, ghazal / sad romantic
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "sad Hindi ghazal, emotional harmonium, gentle tabla, melancholic poetry style, deep sorrow, male vocal",
        "title": "Judai",
        "genre": "world",
        "mood": "sad",
        "bpm": 68,
        "artist_name": "Raj Malhotra",
        "language": "Hindi",
        "lyrics": "Judai ka dard sehna pada\nHar pal mein gham rehna pada\nHarmonium ki awaaz mein\nDil ka dard chehna pada\n\nWo din yaad aate hain\nAansoo bahut sataate hain\nJudai ki raaton mein\nSapne bhi rula jaate hain"
    },
    {
        "prompt": "romantic Hindi music, soft sitar, gentle piano, moonlit night atmosphere, emotional Indian romance",
        "title": "Aankhon Mein",
        "genre": "pop",
        "mood": "romantic",
        "bpm": 78,
        "artist_name": "Raj Malhotra",
        "language": "Hindi",
        "lyrics": "Aankhon mein teri duniya hai\nDil mein teri khushboo hai\nChaand ki roshni mein dekha\nTere chehre ka jaadu hai\n\nSitar ki dhun pe naachein hum\nPiano ke sur pe gaayein hum\nAankhon mein tera aks hai\nDil mein tera ehsaas hai"
    },
    {
        "prompt": "deeply melancholic ghazal, slow harmonium, sorrowful poetry, silence and pain, minimalist sad Indian music",
        "title": "Khamoshi",
        "genre": "world",
        "mood": "sad",
        "bpm": 60,
        "artist_name": "Raj Malhotra",
        "language": "Hindi",
        "lyrics": "Khamoshi mein bhi shor hai\nDil toota hai, kya aur hai\nHarmonium rota hai dheere\nGham ki hai ye dopehere\n\nLafzon se kya kehna hai\nKhamoshi mein hi rehna hai\nDard sunata hai khaamoshi\nJab zubaan pe aaye na hoshi"
    },

    # ═══════════════════════════════════════════════════════════════
    # ANIKA — Hindi female, indie / lofi
    # ═══════════════════════════════════════════════════════════════
    {
        "prompt": "Indian lofi hip hop, soft sitar sample, mellow drums, vinyl crackle, calm night study, Hindi lofi",
        "title": "Neeli Raat",
        "genre": "lofi",
        "mood": "calm",
        "bpm": 80,
        "artist_name": "Anika",
        "language": "Hindi",
        "lyrics": "Neeli raat ka saaya hai\nLofi beats ne ghar basaya hai\nSitar ke sample dheere dheere\nPadhai ki raatein, sapne mere\n\nVinyl crackle aur chaand ki roshni\nShant raat mein milti khushi\nNeeli raat, taron ka saath\nLofi dhun mein meri baat"
    },
    {
        "prompt": "peaceful Indian lofi, gentle flute melody, rain sounds, warm bass, cozy monsoon night atmosphere",
        "title": "Barish Ke Baad",
        "genre": "lofi",
        "mood": "peaceful",
        "bpm": 75,
        "artist_name": "Anika",
        "language": "Hindi",
        "lyrics": "Barish ke baad mitti ki khushbu\nBansuri ki dhun mein chain ka jazba\nBaarish ki boondein khidki pe\nSukoon milta hai is pal mein\n\nGaram chai aur geeli shaam\nLofi beats ka pyaara kaam\nBarish ke baad sab theek hai\nDuniya phir se rang rangeeli hai"
    },
    {
        "prompt": "sad Indian lofi, melancholic sitar loop, tape hiss, slow drums, lonely midnight, nostalgic Hindi",
        "title": "Parchaiyaan",
        "genre": "lofi",
        "mood": "sad",
        "bpm": 72,
        "artist_name": "Anika",
        "language": "Hindi",
        "lyrics": "Parchaiyaan mere saath chalti hain\nPurani yaadein phir se jalti hain\nSitar ki loop mein dard hai\nHar beat mein ek intezaar hai\n\nTape hiss jaise waqt guzre\nDheere dheere sab bikhar jaaye\nParchaiyaan jo saath thi\nAb wo bhi kho gayi kahi"
    },

    # ═══════════════════════════════════════════════════════════════
    # ADDITIONAL DIVERSE TRACKS
    # ═══════════════════════════════════════════════════════════════

    # Lofi tracks with artists
    {
        "prompt": "calm lofi hip hop beat, vinyl crackle, soft piano, mellow drums, study music",
        "title": "Midnight Study Session",
        "genre": "lofi",
        "mood": "calm",
        "bpm": 85,
        "artist_name": "Luna Ray",
        "language": "English",
        "lyrics": "Midnight study, pages turning slow\nVinyl crackle, soft piano glow\nMellow drums keep the rhythm low\nWords and melodies begin to flow\n\nLate night learning, calm and free\nSoft beats helping you and me\nMidnight session, cup of tea\nStudy music, peacefully"
    },
    {
        "prompt": "lofi hip hop, dusty samples, jazz piano chops, boom bap drums, nostalgic",
        "title": "Old School Daydream",
        "genre": "lofi",
        "mood": "relaxing",
        "bpm": 82,
        "artist_name": "Shadow",
        "language": "English",
        "lyrics": "Old school daydream spinning round\nDusty samples, vintage sound\nJazz piano chopped and flipped\nBoom bap drums that never quit\n\nBack to the days of golden tapes\nCassette rewinding, no escapes\nOld school daydream, heads still nod\nTimeless beats from the lofi god"
    },

    # Corporate with artist
    {
        "prompt": "upbeat corporate background, positive energy, acoustic guitar, light piano, motivational, success",
        "title": "Success Story",
        "genre": "corporate",
        "mood": "upbeat",
        "bpm": 120,
        "artist_name": "Nova",
        "language": "English",
        "lyrics": "Every step a building block\nClimbing higher round the clock\nGuitar strumming, piano plays\nBrighter futures, better days\n\nSuccess story being written now\nTaking chances, taking a bow\nPositive energy leading the way\nA brand new chapter starts today"
    },

    # World music
    {
        "prompt": "middle eastern inspired, oud melody, darbuka percussion, atmospheric, mystical desert night",
        "title": "Desert Caravan",
        "genre": "world",
        "mood": "mysterious",
        "bpm": 105,
        "artist_name": "Nova",
        "language": "English",
        "lyrics": "Desert caravan under starlit skies\nOud melody where the eagle flies\nDarbuka drums on the sandy ground\nMystical journey, ancient sound\n\nCamels walking through the moonlit dunes\nAncient melodies, forgotten tunes\nDesert caravan moves through the night\nGuided by the stars' eternal light"
    },
    {
        "prompt": "celtic folk, tin whistle, fiddle, bodhran drum, lively Irish jig, festive pub atmosphere",
        "title": "Green Hills",
        "genre": "world",
        "mood": "upbeat",
        "bpm": 130,
        "artist_name": "Ella Rivers",
        "language": "English",
        "lyrics": "Over the green hills, fiddles play\nTin whistle singing all the day\nBodhran drumming, hip hooray\nIrish jig to chase the grey\n\nRaise a glass in the old pub light\nCeltic folk through the starry night\nGreen hills dancing, what a sight\nLively music burning bright"
    },

    # More sad tracks
    {
        "prompt": "deeply sad piano, solo emotional performance, tears and rain, loneliness, beautiful sorrow",
        "title": "Tears in Silence",
        "genre": "classical",
        "mood": "sad",
        "bpm": 60,
        "artist_name": "Victor Crane",
        "language": "English",
        "lyrics": "Tears in silence fall like rain\nPiano playing through the pain\nEvery note a memory lost\nBeautiful sorrow at any cost\n\nEmpty halls where laughter lived\nAll the love I had to give\nTears in silence, no one hears\nJust the piano and my tears"
    },
    {
        "prompt": "sad ambient, deep reverb, gentle pads, lonely atmosphere, space and solitude, emotional drift",
        "title": "Solitude",
        "genre": "ambient",
        "mood": "sad",
        "bpm": 50,
        "artist_name": "Luna Ray",
        "language": "English",
        "lyrics": "Drifting through the solitude\nGentle pads in quiet mood\nDeep reverb fills the empty space\nMemories of your embrace\n\nAlone among the stars tonight\nSolitude feels almost right\nDrifting slowly, letting go\nSad and beautiful, even so"
    },
]

OUTPUT_DIR = "generated_tracks"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate(duration_seconds=60, count=None, resume=False):
    import torch
    import numpy as np
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import scipy.io.wavfile

    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    metadata_list = []
    existing_titles = set()

    if resume and os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            metadata_list = json.load(f)
            existing_titles = {m["title"] for m in metadata_list}
        print(f"Resuming: {len(existing_titles)} tracks already generated")

    device = "cpu"

    print(f"Loading MusicGen model on {device}...")
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
    model = model.to(device)
    print("Model loaded!")

    # MusicGen-small max is ~30s per generation. For longer tracks,
    # generate multiple 25s chunks and concatenate with crossfade.
    CHUNK_SECONDS = 25
    chunk_tokens = int(CHUNK_SECONDS * 51.2)
    num_chunks = max(1, (duration_seconds + CHUNK_SECONDS - 1) // CHUNK_SECONDS)

    prompts = TRACK_PROMPTS[:count] if count else TRACK_PROMPTS
    generated = 0
    total_to_gen = sum(1 for p in prompts if p["title"] not in existing_titles)

    print(f"Will generate {total_to_gen} tracks (~{duration_seconds}s each, {num_chunks} chunks of {CHUNK_SECONDS}s)")
    est_minutes = total_to_gen * num_chunks * 5  # ~5 min per 25s chunk on CPU
    print(f"Estimated time: ~{est_minutes} minutes on CPU\n")

    for i, track_info in enumerate(prompts):
        if track_info["title"] in existing_titles:
            continue

        generated += 1
        artist = track_info.get("artist_name", "Unknown")
        lang = track_info.get("language", "English")
        print(f"[{generated}/{total_to_gen}] Generating: {track_info['title']} by {artist} [{lang}]")
        print(f"   Genre: {track_info['genre']} | Mood: {track_info['mood']} | BPM: {track_info['bpm']}")
        print(f"   Prompt: {track_info['prompt'][:80]}...")

        try:
            sampling_rate = model.config.audio_encoder.sampling_rate
            audio_chunks = []

            for chunk_idx in range(num_chunks):
                print(f"   Chunk {chunk_idx + 1}/{num_chunks}...", end=" ", flush=True)

                inputs = processor(
                    text=[track_info["prompt"]],
                    padding=True,
                    return_tensors="pt",
                ).to(device)

                audio_values = model.generate(
                    **inputs,
                    max_new_tokens=chunk_tokens,
                    do_sample=True,
                    guidance_scale=3.0,
                )

                chunk_data = audio_values[0, 0].cpu().numpy()
                audio_chunks.append(chunk_data)
                chunk_dur = len(chunk_data) / sampling_rate
                print(f"{chunk_dur:.1f}s", flush=True)

            # Concatenate chunks with crossfade
            if len(audio_chunks) == 1:
                audio_data = audio_chunks[0]
            else:
                crossfade_samples = int(sampling_rate * 2)  # 2s crossfade
                audio_data = audio_chunks[0]
                for chunk in audio_chunks[1:]:
                    overlap = min(crossfade_samples, len(audio_data), len(chunk))
                    fade_out = np.linspace(1.0, 0.0, overlap).astype(np.float32)
                    fade_in = np.linspace(0.0, 1.0, overlap).astype(np.float32)
                    # Crossfade the overlapping region
                    crossfaded = audio_data[-overlap:] * fade_out + chunk[:overlap] * fade_in
                    audio_data = np.concatenate([audio_data[:-overlap], crossfaded, chunk[overlap:]])

            base_name = f"{track_info['genre']}_{track_info['title'].lower().replace(' ', '_')}"
            wav_filename = f"{base_name}.wav"
            wav_path = os.path.join(OUTPUT_DIR, wav_filename)

            scipy.io.wavfile.write(wav_path, rate=sampling_rate, data=audio_data)

            actual_duration = len(audio_data) / sampling_rate
            file_size = os.path.getsize(wav_path)

            metadata = {
                "filename": wav_filename,
                "title": track_info["title"],
                "genre": track_info["genre"],
                "mood": track_info["mood"],
                "bpm": track_info["bpm"],
                "duration": int(actual_duration),
                "prompt": track_info["prompt"],
                "lyrics": track_info.get("lyrics", ""),
                "artist_name": track_info.get("artist_name", ""),
                "language": track_info.get("language", "English"),
            }
            metadata_list.append(metadata)

            with open(meta_path, "w") as f:
                json.dump(metadata_list, f, indent=2)

            print(f"   Saved: {wav_filename} ({file_size // 1024} KB, {actual_duration:.1f}s)\n")

        except Exception as e:
            print(f"   ERROR: {e}\n")
            continue

    print(f"\nDone! Generated {generated} new tracks ({len(metadata_list)} total)")


def import_to_django():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django
    django.setup()

    from django.core.files import File
    from tracks.models import Track, Genre, Mood

    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    if not os.path.exists(meta_path):
        print("No metadata.json found.")
        return

    with open(meta_path, "r") as f:
        metadata_list = json.load(f)

    imported = 0
    for meta in metadata_list:
        filepath = os.path.join(OUTPUT_DIR, meta["filename"])
        if not os.path.exists(filepath):
            continue
        if Track.objects.filter(title=meta["title"]).exists():
            continue

        genre = Genre.objects.filter(slug=meta["genre"]).first()
        mood = Mood.objects.filter(slug=meta["mood"]).first()

        # Look up lyrics from TRACK_PROMPTS if not in metadata
        lyrics = meta.get("lyrics", "")
        if not lyrics:
            for tp in TRACK_PROMPTS:
                if tp["title"] == meta["title"]:
                    lyrics = tp.get("lyrics", "")
                    break

        # Look up artist_name and language from TRACK_PROMPTS if not in metadata
        artist_name = meta.get("artist_name", "")
        language = meta.get("language", "English")
        if not artist_name:
            for tp in TRACK_PROMPTS:
                if tp["title"] == meta["title"]:
                    artist_name = tp.get("artist_name", "")
                    language = tp.get("language", "English")
                    break

        with open(filepath, "rb") as audio_file:
            track = Track(
                title=meta["title"],
                genre=genre,
                mood=mood,
                bpm=meta.get("bpm"),
                duration=meta.get("duration", 60),
                description=meta.get("prompt", ""),
                lyrics=lyrics,
                artist_name=artist_name,
                language=language,
                tags=f"{meta['genre']}, {meta['mood']}",
                is_active=True,
                is_featured=(imported % 5 == 0),
            )
            track.audio_file.save(meta["filename"], File(audio_file), save=True)

        print(f"  Imported: {meta['title']} by {artist_name} [{language}] ({meta['genre']}/{meta['mood']})")
        imported += 1

    print(f"\nImported {imported} new tracks. Total in DB: {Track.objects.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate music locally with MusicGen")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds (default: 60)")
    parser.add_argument("--count", type=int, default=None, help="Number of tracks (default: all)")
    parser.add_argument("--resume", action="store_true", help="Skip existing tracks")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Import to Django after")
    parser.add_argument("--import-only", action="store_true", help="Only import, no generation")
    args = parser.parse_args()

    if args.import_only:
        import_to_django()
    else:
        generate(duration_seconds=args.duration, count=args.count, resume=args.resume)
        if args.do_import:
            import_to_django()
