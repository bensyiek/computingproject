pokemonInDraft = ['Charizard',
                  'Amoonguss',
                  'Electivire',
                  'Feraligatr',
                  'Garchomp','Gardevoir','Gengar',
                  'Hydreigon',
                  'Infernape',
                  'Kyurem-B',
                  'Lucario',
                  'Magnezone',
                  'Rotom-H','Rotom-W',
                  'Scizor',
                  'Quagsire',
                  'Tyranitar']

typeColor = {
    'Grass' : 'SpringGreen2',
    'Water' : 'SteelBlue1',
    'Fire' : 'tomato',
    'Dark' : 'gray50',
    'Psychic' : 'maroon1',
    'Fighting' : 'brown',
    'Rock' : 'burlywood4',
    'Ground' : 'burlywood3',
    'Ice' : 'PaleTurquoise1',
    'Dragon' : 'slate blue',
    'Fairy' : 'pink',
    'Normal' : 'beige',
    'Poison' : 'magenta3',
    'Steel' : 'gray64',
    'Electric' : 'yellow',
    'Flying' : 'light blue',
    'Ghost':'purple',
    'Bug':'light green'
    }

userSwitchMessages = ['%s! Return!','Good job, come back %s!',
                           'Ok, come back, %s!',"That's enough, %s."]
userSendInMessages = ["Your foe's weak, gettem, %s!", "Go! %s!", "Show 'em who's boss, %s!",
                      "Give it everything you've got, %s!","%s! I choose you!"]

backgrounds = {
    'route' : {'filePath' : 'assets/routeBackground.png', 'bgColor' : 'green'},
    'indoor' : {'filePath' : 'assets/indoorBackground.png','bgColor' : 'grey'}
    }

assets = {
    'selectionBox' : 'assets/drafting/selectionBox.png',##these until the next comment are resources for drafting
    'sBoxTR' : 'assets/drafting/selectionBoxTR.png',
    'sBoxTL' : 'assets/drafting/selectionBoxTL.png',
    'sBoxBR' : 'assets/drafting/selectionBoxBR.png',
    'sBoxBL' : 'assets/drafting/selectionBoxBL.png',
    'begin' : 'assets/drafting/begin.png',
    'draft' : 'assets/drafting/draft.png',
    'triangle' : 'assets/trianglePointer.jpg', ##the rest are for use in battlegui
    'fightButton' : 'assets/fightButton.png',
    'grass' : 'assets/Basic_Grass.png',
    'indoor-enemy' : 'assets/indoor-enemy-platform.png',
    'indoor-user' : 'assets/indoor-user-platform.png',
    'EnemyHP' : 'assets/inbattle/EnemyHPNewNew.png',
    'UserHP' : 'assets/inbattle/UserHPNew.png',
    'greenBar' : 'assets/inbattle/Green.png',
    'yellowBar' : 'assets/inbattle/Yellow.png',
    'redBar' : 'assets/inbattle/Red.png'
    }

trainerSprites = {'Blue' : 'assets/trainers/Blue.gif','Ben':'assets/trainers/Ben.png','Dalton':'assets/trainers/Dalton.png','Pedro':'assets/trainers/Pedro.png','Yuriy':'assets/trainers/Yuriy.png'}
trainerBackSprites = {'Ethan' : 'assets/trainers/BACK-Ethan.gif'}
pokeballs = {'Masterball' : 'assets/pokeballs/masterball.gif','Pokeball' : 'assets/pokeballs/pokeball.gif'}
throwpokeballs = {'Pokeball' : 'assets/pokeballs/throw-pokeball.gif'}
toBe = '''To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them. To die—to sleep, No more; and by a sleep to say we end The heart-ache and the thousand natural shocks That flesh is heir to: 'tis a consummation Devoutly to be wish'd. To die, to sleep; To sleep, perchance to dream—ay, there's the rub: For in that sleep of death what dreams may come, When we have shuffled off this mortal coil, Must give us pause—there's the respect That makes calamity of so long life. For who would bear the whips and scorns of time, Th'oppressor's wrong, the proud man's contumely, The pangs of dispriz'd love, the law's delay, The insolence of office, and the spurns That patient merit of th'unworthy takes, When he himself might his quietus make With a bare bodkin? Who would fardels bear, To grunt and sweat under a weary life, But that the dread of something after death, The undiscovere'd country, from whose bourn No traveller returns, puzzles the will, And makes us rather bear those ills we have Than fly to others that we know not of? Thus conscience does make cowards of us all, And thus the native hue of resolution Is sicklied o'er with the pale cast of thought, And enterprises of great pitch and moment With this regard their currents turn awry And lose the name of action.'''

attacks = {'fighting' : 'assets/attacks/fp/fightingPhysical.png'}

pokemon = {'Charizard' : 'assets/pokemon/charizard.gif'}
pokemonBackSprites = {'Charizard' : 'assets/pokemon/charizard-back.png'}
icons = {'Charizard':'assets/pokemon/charizard_icon.gif','False':'assets/none.png'}

for x in pokemonInDraft:
    pokemon[x] = 'assets/pokemon/'+x.lower()+'.gif'
    pokemonBackSprites[x] = 'assets/pokemon/'+x.lower()+'-back.png'
    icons[x] = 'assets/pokemon/'+x.lower()+'_icon.gif'


#Swampert Moves: 'Earthquake', 'Ice Punch', 'Superpower', 'Waterfall',
moveInfo = {
    '<Template>' : {'type' : '', 'category' : '', 'priority' : 0, 'power' : 0, 'pp' : 1, 'accuracy' : 0, 'description' : ""},

    ##A
    'Acrobatics' : {'type' : 'Flying', 'category' : 'Physical', 'priority' : 0, 'power' : 55, 'pp' : 100, 'accuracy' : 100, 'description' : "User nimbly strikes the foe."},
    'Aerial Ace' : {'type' : 'Flying', 'category' : 'Physical', 'priority' : 0, 'power' : 60, 'pp' : 20, 'accuracy' : 900, 'description' : "An extremely fast attack against one target. It can’t be evaded."},
    'Amnesia' : {'type' : 'Psychic', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 20, 'accuracy' : 900, 'description' : 'User forgets about the world. Sharply raises the user’s Sp. Defense.'},
    'Aqua Jet' : {'type' : 'Water', 'category' : 'Physical', 'priority' : 1, 'power' : 40, 'pp' : 20, 'accuracy' : 100, 'description' : "User lunges at the foe at very high speed. It is sure to strike first."},
    'Aqua Tail' : {'type' : 'Water', 'category' : 'Physical', 'priority' : 0, 'power' : 90, 'pp' : 10, 'accuracy' : 90, 'description' : 'User attacks with its tail as if it were a wave in a raging storm.'},
    'Aura Sphere' : {'type' : 'Fighting', 'category' : 'Special', 'priority' : 0, 'power' : 80, 'pp' : 20, 'accuracy' : 900, 'description' : "User releases powerful aura from its body. Can't miss."},

    ##B
    'Blaze Kick' : {'type' : 'Fire', 'category' : 'Physical', 'priority' : 0, 'power' : 85, 'pp' : 10, 'accuracy' : 90, 'description' : "A kick with a high critical-hit ratio. May cause a burn."},
    'Blizzard' : {'type' : 'Ice', 'category' : 'Special', 'priority' : 0, 'power' : 110, 'pp' : 1, 'accuracy' : 70, 'description' : "Foe is blasted with a blizzard. May cause freezing."},
    'Bone Rush' : {'type' : 'Ground', 'category' : 'Physical', 'priority' : 0, 'power' : 25, 'pp' : 10, 'accuracy' : 90, 'description' : "User strikes foe with a bone in hand two to five times."},
    'Brick Break' : {'type' : 'Fighting', 'category' : 'Physical', 'priority' : 0, 'power' : 75, 'pp' : 15, 'accuracy' : 100, 'description' : "	Destroys barriers such as Reflect and causes damage."},
    'Bullet Punch' : {'type' : 'Steel', 'category' : 'Physical', 'priority' : 1, 'power' : 40, 'pp' : 40, 'accuracy' : 100, 'description' : "A lighting-fast punch with an iron fist. Always goes first."},

    ##C
    'Calm Mind' : {'type' : 'Psychic', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 20, 'accuracy' : 900, 'description' : "User focuses its mind to raise their Sp. Attack and Sp. Defense."},
    'Chip Away' : {'type' : 'Dark', 'category' : 'Physical', 'priority' : 0, 'power' : 70, 'pp' : 20, 'accuracy' : 100, 'description' : "Foe’s stat changes don’t affect this attack's damage."},
    'Clear Smog' : {'type' : 'Poison', 'category' : 'Special', 'priority' : 0, 'power' : 50, 'pp' : 15, 'accuracy' : 900, 'description' : "Uesr throws a clump of special mud. Foe's stat changes are reset."},
    'Close Combat' : {'type' : 'Fighting', 'category' : 'Physical', 'priority' : 0, 'power' : 120, 'pp' : 5, 'accuracy' : 100, 'description' : "User attacks foe in close without guarding itself. Lowers user’s Defense and Sp. Defense."},
    'Crunch' : {'type' : 'Dark', 'category' : 'Physical', 'priority' : 0, 'power' : 80, 'pp' : 15, 'accuracy' : 100, 'description' : "Foe is crunched with sharp fangs. It may lower the foe’s Defense."},

    ##D
    'Dark Pulse' : {'type' : 'Dark', 'category' : 'Special', 'priority' : 0, 'power' : 80, 'pp' : 15, 'accuracy' : 100, 'description' : "User releases a horrible aura imbued with dark thoughts. May cause flinching."},
    'Discharge' : {'type' : 'Electric', 'category' : 'Special', 'priority' : 0, 'power' : 80, 'pp' : 15, 'accuracy' : 100, 'description' : "A loose flare of electricity strikes the foe. May cause paralysis."},
    'Double Team' : {'type' : 'Normal', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 15, 'accuracy' : 900, 'description' : "The user creates illusory copies of itself to raise its evasiveness."},
    'Dual Chop' : {'type' : 'Dragon', 'category' : 'Physical', 'priority' : 0, 'power' : 40, 'pp' : 15, 'accuracy' : 90, 'description' : "Foe is hit with brutal strikes. Hits twice."},
    'Draco Meteor' : {'type' : 'Dragon', 'category' : 'Special', 'priority' : 0, 'power' : 130, 'pp' : 1, 'accuracy' : 90, 'description' : "Comets are summoned from the sky. Sharply lowers user's Sp. Attack"},
    'Dragon Claw' : {'type' : 'Dragon', 'category' : 'Physical', 'priority' : 0, 'power' : 80, 'pp' : 15, 'accuracy' : 100, 'description' : "User slashes foe with sharp claws."},
    'Dragon Dance' : {'type' : 'Dragon', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 20, 'accuracy' : 900, 'description' : "A mystical dance that ups Attack and Speed."},
    'Dragon Pulse' : {'type' : 'Dragon', 'category' : 'Special', 'priority' : 0, 'power' : 85, 'pp' : 10, 'accuracy' : 100, 'description' : "Foe is hit by a shock wave generated by the user's mouth."},
    'Dragon Rush' : {'type' : 'Dragon', 'category' : 'Physical', 'priority' : 0, 'power' : 100, 'pp' : 10, 'accuracy' : 75, 'description' : "With overwhelming menace, user tackles foe. May cause flinching."},
    'Drain Punch' : {'type' : 'Fighting', 'category' : 'Physical', 'priority' : 0, 'power' : 75, 'pp' : 10, 'accuracy' : 100, 'description' : "An energy-draining punch. User steals HP from foe."},

    ##E
    'Earth Power' : {'type' : 'Ground', 'category' : 'Special', 'priority' : 0, 'power' : 90, 'pp' : 10, 'accuracy' : 100, 'description' : "User makes ground under foe erupt. May lower foe's Sp. Defense."},
    'Earthquake' : {'type' : 'Ground', 'category' : 'Physical', 'priority' : 0, 'power' : 100, 'pp' : 10, 'accuracy' : 100, 'description' : 'The user sets off an earthquake that strikes every Pokémon around it.'},
    'Electro Ball' : {'type' : 'Electric', 'category' : 'Special', 'priority' : 0, 'power' : 40, 'pp' : 10, 'accuracy' : 100, 'description' : "This attack's power increases drastically if user is much faster than foe."},
    'Energy Ball' : {'type' : 'Grass', 'category' : 'Special', 'priority' : 0, 'power' : 90, 'pp' : 10, 'accuracy' : 100, 'description' : "User draws power from nature and fires it at the foe. May lower foe's Sp. Defense."},
    'Extreme Speed' : {'type' : 'Normal', 'category' : 'Physical', 'priority' : 2, 'power' : 80, 'pp' : 5, 'accuracy' : 100, 'description' : "A blindingly speedy charge attack that always goes before any other."},

    ##F
    'Facade' : {'type' : 'Normal', 'category' : 'Physical', 'priority' : 0, 'power' : 70, 'pp' : 20, 'accuracy' : 100, 'description' : 'An attack that is boosted if user is burned, poisoned, or paralyzed.'},
    'Fake Out' : {'type' : 'Normal', 'category' : 'Physical', 'priority' : 3, 'power' : 40, 'pp' : 10, 'accuracy' : 100, 'description' : "An attack that hits first and causes flinching. Usable only on 1st turn."},
    'Fire Blast' : {'type' : 'Fire', 'category' : 'Special', 'priority' : 0, 'power' : 110, 'pp' : 5, 'accuracy' : 85, 'description' : "Incinerates everything it strikes. May cause a burn."},
    'Fire Fang' : {'type' : 'Fire', 'category' : 'Physical', 'priority' : 0, 'power' : 65, 'pp' : 1, 'accuracy' : 95, 'description' : "A fiery bite. May burn foe or cause flinching."},
    'Fire Punch' : {'type' : 'Fire', 'category' : 'Physical', 'priority' : 0, 'power' : 75, 'pp' : 15, 'accuracy' : 100, 'description' : "A fiery punch that may burn the foe."},
    'Flamethrower' : {'type' : 'Fire', 'category' : 'Special', 'priority' : 0, 'power' : 90, 'pp' : 15, 'accuracy' : 100, 'description' : "Foe is scorched with intense flames. May cause burn."},
    'Flash Cannon' : {'type':'Steel','category' : 'Special', 'priority' : 0, 'power' : 80, 'pp' : 10, 'accuracy' : 100, 'description' : "User gathers light energy and releases it at once. May lower foe's Sp. Defense."},
    'Focus Blast' : {'type' : 'Fighting', 'category' : 'Special', 'priority' : 0, 'power' : 120, 'pp' : 1, 'accuracy' : 70, 'description' : "User heightens and unleashes its mental power. May lower foe's Sp. Defense."},
    'Freeze Shock' : {'type' : 'Ice', 'category' : 'Physical', 'priority' : 0, 'power' : 140, 'pp' : 5, 'accuracy' : 90, 'description' : "On the second turn, foe is hit with electrically charged ice. May cause paralysis."},
    'Fury Cutter' : {'type' : 'Bug', 'category' : 'Physical', 'priority' : 0, 'power' : 40, 'pp' : 20, 'accuracy' : 95, 'description' : "An attack that grows stronger on each successive hit."},
    'Fusion Bolt' : {'type' : 'Electric', 'category' : 'Physical', 'priority' : 0, 'power' : 100, 'pp' : 5, 'accuracy' : 100, 'description' : "User unleashes its frightening electrical energy."},

    ##G
    'Giga Drain' : {'type' : 'Grass', 'category' : 'Special', 'priority' : 0, 'power' : 75, 'pp' : 10, 'accuracy' : 100, 'description' : "An attack that steals half the damage inflicted."},
    'Gunk Shot' : {'type' : 'Poison', 'category' : 'Physical', 'priority' : 0, 'power' : 120, 'pp' : 5, 'accuracy' : 80, 'description' : "User throws garbage at foe. May poison foe."},

    ##H
    'Hex' : {'type' : 'Ghost', 'category' : 'Special', 'priority' : 0, 'power' : 65, 'pp' : 10, 'accuracy' : 100, 'description' : "A malicious curse that gets stronger if the foe has a status condition."},
    'Hydro Pump' : {'type' : 'Water', 'category' : 'Special', 'priority' : 0, 'power' : 110, 'pp' : 5, 'accuracy' : 80, 'description' : "Blasts water at high pressure to strike the foe."},
    'Hyper Voice' : {'type' : 'Normal', 'category' : 'Special', 'priority' : 0, 'power' : 90, 'pp' : 10, 'accuracy' : 100, 'description' : "A loud attack that uses sound waves to injure."},
    'Hypnosis' : {'type' : 'Psychic', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 20, 'accuracy' : 60, 'description' : "A hypnotizing move that may induce sleep"},

    ##I
    'Ice Beam' : {'type' : 'Ice', 'category' : 'Special', 'priority' : 0, 'power' : 90, 'pp' : 10, 'accuracy' : 100, 'description' : "Blasts the foe with an icy beam that may freeze it."},
    'Ice Fang' : {'type' : 'Ice', 'category' : 'Physical', 'priority' : 0, 'power' : 65, 'pp' : 1, 'accuracy' : 95, 'description' : "An icy bite. May freeze foe or cause flinching."},
    'Ice Punch' : {'type' : 'Ice', 'category' : 'Physical', 'priority' : 0, 'power' : 75, 'pp' : 15, 'accuracy' : 100, 'description' : "An icy punch that may freeze the foe."},
    'Icicle Spear' : {'type' : 'Ice', 'category' : 'Physical', 'priority' : 0, 'power' : 25, 'pp' : 10, 'accuracy' : 90, 'description' : "Throws piercing icicles at the foe 2 to 5 times in a row."},
    'Iron Head' : {'type' : 'Steel', 'category' : 'Physical', 'priority' : 0, 'power' : 80, 'pp' : 15, 'accuracy' : 100, 'description' : "Foe is slammed with a steel-hard head. May cause flinching."},
    'Iron Tail' : {'type' : 'Steel', 'category' : 'Physical', 'priority' : 0, 'power' : 100, 'pp' : 15, 'accuracy' : 75, 'description' : "An attack with a rock-hard tail. May lower foe's Defense."},
    'Iron Defense' : {'type' : 'Steel', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 15, 'accuracy' : 900, 'description' : "Hardens the body’s surface to sharply raise Defense."},

    ##L
    'Light Screen' : {'type' : 'Psychic', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 30, 'accuracy' : 900, 'description' : "Creates a wall of light that lowers incoming Sp. Attack damage."},

    ##M
    'Mach Punch' : {'type' : 'Fighting', 'category' : 'Physical', 'priority' : 1, 'power' : 40, 'pp' : 30, 'accuracy' : 100, 'description' : "A fast punch that lands first."},
    'Magical Leaf' : {'type' : 'Grass', 'category' : 'Special', 'priority' : 0, 'power' : 60, 'pp' : 1, 'accuracy' : 900, 'description' : "User scatters curious leaves that chase the foe. This attack will not miss."},
    'Magnet Rise' : {'type' : 'Electric', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 10, 'accuracy' : 900, 'description' : "User becomes immune to Ground-type moves until they switch out."},
    'Metal Claw' : {'type' : 'Steel', 'category' : 'Physical', 'priority' : 0, 'power' : 50, 'pp' : 35, 'accuracy' : 95, 'description' : "Foe is raked with steel claws. May also raise the user’s Attack stat."},
    'Moonblast' : {'type' : 'Fairy', 'category' : 'Special', 'priority' : 0, 'power' : 95, 'pp' : 15, 'accuracy' : 100, 'description' : "User attacks foe with power of the moon. May lower foe’s Sp. Attack."},

    ##N
    'Night Slash' : {'type' : 'Dark', 'category' : 'Physical', 'priority' : 0, 'power' : 70, 'pp' : 15, 'accuracy' : 100, 'description' : "User slashes foe at an opportune time. High critical-hit ratio."},

    ##O
    'Overheat' : {'type' : 'Fire', 'category' : 'Special', 'priority' : 0, 'power' : 130, 'pp' : 5, 'accuracy' : 90, 'description' : "An intense attack that also harshly reduces the user’s Sp. Attack stat."},

    ##P
    'Protect' : {'type' : 'Normal', 'category' : 'Status', 'priority' : 4, 'power' : 0, 'pp' : 10, 'accuracy' : 900, 'description' : "Enables the user to evade all attacks. It may fail if used in succession."},
    'Psychic' : {'type' : 'Psychic', 'category' : 'Special', 'priority' : 0, 'power' : 90, 'pp' : 10, 'accuracy' : 100, 'description' : "A powerful psychic attack that may lower foe's Sp. Defense"},
    'Punishment' : {'type' : 'Dark', 'category' : 'Physical', 'priority' : 0, 'power' : 60, 'pp' : 5, 'accuracy' : 100, 'description' : "This attack punishes foe's stat increases."},
    'Pursuit' : {'type' : 'Dark', 'category' : 'Physical', 'priority' : 0, 'power' : 40, 'pp' : 20, 'accuracy' : 100, 'description' : "Inflicts double damage if used on a foe switching out."},

    ##R
    'Reflect' : {'type' : 'Psychic', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 30, 'accuracy' : 900, 'description' : "Creates a wall of light that lowers incoming Attack damage."},
    'Roar' : {'type' : 'Normal', 'category' : 'Status', 'priority' : -8, 'power' : 0, 'pp' : 1, 'accuracy' : 900, 'description' : "Scares the foe, forcing the enemy trainer to swap Pokemon at random. Moves last."},
    'Rock Blast' : {'type' : 'Rock', 'category' : 'Physical', 'priority' : 0, 'power' : 25, 'pp' : 10, 'accuracy' : 90, 'description' : "Hurls boulders at the foe 2 to 5 times in a row."},
    'Rock Slide' : {'type' : 'Rock', 'category' : 'Physical', 'priority' : 0, 'power' : 75, 'pp' : 10, 'accuracy' : 90, 'description' : "Large boulders are hurled. May cause flinching."},

    ##S
    'Scary Face' : {'type' : 'Normal', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 10, 'accuracy' : 100, 'description' : "Frightens with a scary face to sharply reduce Speed."},
    'Screech' : {'type' : 'Normal', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 40, 'accuracy' : 85, 'description' : "Emits a screech to sharply reduce the foe’s Defense."},
    'Shadow Ball' : {'type' : 'Ghost', 'category' : 'Special', 'priority' : 0, 'power' : 80, 'pp' : 15, 'accuracy' : 100, 'description' : "A shadowy blob is hurled at the foe. May lower foe's Sp. Defense."},
    'Shadow Claw' : {'type' : 'Ghost', 'category' : 'Physical', 'priority' : 0, 'power' : 70, 'pp' : 15, 'accuracy' : 100, 'description' : "User slashes with a sharp claw. Has a high critical-hit ratio."},
    'Slash' : {'type' : 'Normal', 'category' : 'Physical', 'priority' : 0, 'power' : 70, 'pp' : 20, 'accuracy' : 100, 'description' : "Foe is slashed with claws, etc. Has a high critical-hit ratio."},
    'Sludge Bomb' : {'type' : 'Poison', 'category' : 'Special', 'priority' : 0, 'power' : 90, 'pp' : 10, 'accuracy' : 100, 'description' : "Sludge is hurled to inflict damage. May also poison."},
    'Sludge Wave' : {'type' : 'Poison', 'category' : 'Special', 'priority' : 0, 'power' : 95, 'pp' : 10, 'accuracy' : 100, 'description' : "User swamps area with poisonous sludge. May also poison."},
    'Solar Beam' : {'type' : 'Grass', 'category' : 'Special', 'priority' : 0, 'power' : 120, 'pp' : 10, 'accuracy' : 100, 'description' : "Absorbs light in one turn, then attacks next turn."},
    'Spore' : {'type' : 'Grass', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 10, 'accuracy' : 100, 'description' : "Lulls the foe to sleep."},
    'Stone Edge' : {'type' : 'Rock', 'category' : 'Physical', 'priority' : 0, 'power' : 100, 'pp' : 5, 'accuracy' : 80, 'description' : "User stabs the foe with stones. High critical-hit ratio."},
    'Superpower' : {'type' : 'Fighting', 'category' : 'Physical', 'priority' : 0, 'power' : 120, 'pp' : 5, 'accuracy' : 100, 'description' : "A powerful attack, but it also lowers the user’s Attack and Defense stats."},
    'Swords Dance' : {'type' : 'Normal', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 20, 'accuracy' : 900, 'description' : "A fighting dance that sharply raises Attack."},
    'Synthesis' : {'type' : 'Grass', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 5, 'accuracy' : 900, 'description' : "Restores the user’s HP."},

    ##T
    'Tackle' : {'type' : 'Normal', 'category' : 'Physical', 'priority' : 0, 'power' : 40, 'pp' : 35, 'accuracy' : 95, 'description' : "The user rams its body into its opponent."},
    'Taunt' : {'type' : 'Dark', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 20, 'accuracy' : 100, 'description' : "Taunts the foe into only using attack moves."}, 
    'Thunder' : {'type' : 'Electric', 'category' : 'Special', 'priority' : 0, 'power' : 110, 'pp' : 10, 'accuracy' : 70, 'description' : "A brutal lightning attack that may paralyze foe."},
    'Thunderbolt' : {'type' : 'Electric', 'category' : 'Special', 'priority' : 0, 'power' : 90, 'pp' : 15, 'accuracy' : 100, 'description' : "A strong electrical attack that may paralyze the foe."},
    'Thunder Fang' : {'type' : 'Electric', 'category' : 'Physical', 'priority' : 0, 'power' : 65, 'pp' : 15, 'accuracy' : 95, 'description' : "An ionizing bite. May paralyze foe or cause flinching."},
    'Thunder Punch' : {'type' : 'Electric', 'category' : 'Physical', 'priority' : 0, 'power' : 75, 'pp' : 15, 'accuracy' : 100, 'description' : "An electrified punch that may paralyze the foe."},
    'Thunder Wave' : {'type' : 'Electric', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 20, 'accuracy' : 900, 'description' : 'A weak jolt of electricity that paralyzes the foe.'},
    'Toxic' : {'type' : 'Poison', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 10, 'accuracy' : 90, 'description' : 'Poisons the foe with an intensifying toxin.'},
    'Trick Room' : {'type' : 'Psychic', 'category' : 'Status', 'priority' : -7, 'power' : 0, 'pp' : 5, 'accuracy' : 900, 'description' : "User creates a bizarre area in which slower Pokémon get to move first for five turns."},

    ##V
    'Venoshock' : {'type' : 'Poison', 'category' : 'Special', 'priority' : 0, 'power' : 65, 'pp' : 10, 'accuracy' : 100, 'description' : "Foe is drenched in a poisonous liquid. Deals double damage if foe poisoned."},

    ##W
    '<Template>' : {'type' : '', 'category' : '', 'priority' : 0, 'power' : 0, 'pp' : 1, 'accuracy' : 0, 'description' : ""},
    'Wish' : {'type' : 'Normal', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 10, 'accuracy' : 900, 'description' : "A self-healing move that restores restores HP on the next turn."},
    'Will-O-Wisp' : {'type' : 'Fire', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 15, 'accuracy' : 85, 'description' : "A sinister, bluish white flame is shot at the foe to inflict a burn."},

    ##X
    'X-Scissor' : {'type' : 'Bug', 'category' : 'Physical', 'priority' : 0, 'power' : 80, 'pp' : 15, 'accuracy' : 100, 'description' : "User slashes at foe by crossing its claws, etc. as though they were scissors"},

    ##Y
    'Yawn' : {'type' : 'Normal', 'category' : 'Status', 'priority' : 0, 'power' : 0, 'pp' : 10, 'accuracy' : 900, 'description' : 'A huge yawn lulls the foe into falling asleep on the next turn.'},

    ##Z
    'Zap Cannon' : {'type' : 'Electric', 'category' : 'Special', 'priority' : 0, 'power' : 120, 'pp' : 5, 'accuracy' : 50, 'description' : "Powerful but inaccurate electric blast that causes paralysis."},
    'Zen Headbutt' : {'type' : 'Psychic', 'category' : 'Physical', 'priority' : 0, 'power' : 80, 'pp' : 15, 'accuracy' : 90, 'description' : "User focuses its will and rams its foe. May cause flinching."},
    }

pkmnInfo = {
    '<Template>' : {'stats':(0,0,0,0,0,0),'type1':'','type2':'','moves':[]},
    'Charizard' : {'stats' : (45,49,49,65,65,45), 'type1' : 'Grass', 'type2' : 'Poison', 'moves' : ['Roar','Roar','Pursuit','Pursuit']},

    ##A
    'Amoonguss' : {'stats':(114,85,70,85,80,30),'type1':'Grass','type2':'Poison','moves':['Clear Smog','Energy Ball','Giga Drain','Protect','Sludge Bomb','Spore','Synthesis','Toxic','Venoshock']},

    ##E
    'Electivire' : {'stats':(75,123,67,95,85,95),'type1':'Electric','type2':'','moves':['Brick Break', 'Discharge', 'Dual Chop', 'Earthquake', 'Electro Ball', 'Fire Punch', 'Ice Punch', 'Screech', 'Iron Tail', 'Thunderbolt', 'Thunder', 'Thunder Punch']},

    ##F
    'Feraligatr' : {'stats':(85,105,100,79,83,78),'type1':'Water','type2':'','moves':['Aqua Jet', 'Aqua Tail','Chip Away','Crunch','Dragon Dance','Ice Punch','Iron Tail','Metal Claw','Slash','Superpower']},

    ##G
    'Garchomp' : {'stats':(108,130,95,80,85,102),'type1':'Dragon','type2':'Ground','moves':['Aqua Tail', 'Crunch', 'Draco Meteor', 'Dragon Claw', 'Dragon Rush', 'Earthquake', 'Fire Blast', 'Fire Fang', 'Roar', 'Stone Edge', 'Swords Dance','Toxic']},
    'Gardevoir' : {'stats':(68,65,65,125,115,80),'type1':'Psychic','type2':'Fairy','moves':['Calm Mind','Energy Ball','Light Screen','Magical Leaf','Moonblast','Protect','Psychic','Reflect','Shadow Ball','Thunderbolt','Trick Room','Wish','Will-O-Wisp']},
    'Gengar' : {'stats':(60,60,60,130,75,110),'type1':'Ghost','type2':'Poison','moves':['Dark Pulse','Energy Ball','Hex','Hypnosis','Psychic','Shadow Ball','Sludge Bomb','Sludge Wave','Taunt','Venoshock',]},

    ##H
    'Hydreigon' : {'stats':(92,105,90,125,90,98),'type1':'Dark','type2':'Dragon','moves':['Crunch','Dark Pulse','Draco Meteor','Dragon Pulse','Dragon Rush','Earth Power','Earthquake','Facade','Flamethrower','Flash Cannon','Fire Blast','Hyper Voice','Scary Face','Stone Edge','Thunder Wave','Toxic']},

    ##I
    'Infernape' : {'stats':(76,104,71,104,71,108),'type1':'Fire','type2':'Fighting','moves':['Acrobatics','Aerial Ace','Blaze Kick','Close Combat','Dual Chop','Fake Out','Fire Punch','Gunk Shot','Iron Tail','Mach Punch','Punishment','Taunt','Thunder Punch']},

    ##K
    'Kyurem-B' : {'stats':(125,170,100,120,90,95),'type1':'Dragon','type2':'Ice','moves':['Dragon Claw','Dragon Dance','Freeze Shock','Fusion Bolt','Icicle Spear','Slash','Shadow Claw','Zen Headbutt']},

    ##L
    'Lucario' : {'stats':(70,110,70,115,70,90),'type1':'Fighting','type2':'Steel','moves':['Aura Sphere','Blaze Kick','Bone Rush','Close Combat','Calm Mind','Dark Pulse','Dragon Pulse','Drain Punch','Flash Cannon','Ice Punch','Iron Tail','Metal Claw','Screech','Swords Dance',]},
    
    ##M
    'Magnezone' : {'stats':(70,70,115,130,90,60),'type1':'Electric','type2':'Steel','moves':['Discharge','Double Team','Flash Cannon','Iron Defense','Light Screen','Magnet Rise','Reflect','Thunder Wave','Zap Cannon']},

    ##Q
    'Quagsire' : {'stats' : (95,85,85,65,65,35),'type1':'Water','type2':'Ground','moves':['Amnesia','Aqua Tail','Earthquake','Facade','Iron Tail','Protect','Toxic','Yawn']},

    ##R
    'Rotom-W' : {'stats':(50,65,107,105,107,86),'type1':'Electric','type2':'Water','moves':['Double Team','Electro Ball','Thunder Wave','Hex','Discharge','Thunder Wave','Protect','Light Screen','Reflect','Dark Pulse','Thunderbolt','Hydro Pump']},
    'Rotom-H' : {'stats':(50,65,107,105,107,86),'type1':'Electric','type2':'Fire','moves':['Double Team','Electro Ball','Thunder Wave','Hex','Discharge','Thunder Wave','Protect','Light Screen','Reflect','Dark Pulse','Thunderbolt','Overheat']},

    ##S
    'Scizor' : {'stats':(70,130,100,55,70,65),'type1':'Bug','type2':'Steel','moves':['Aerial Ace','Bullet Punch','Double Team','Fury Cutter','Iron Defense','Metal Claw','Night Slash','Pursuit','Superpower','Swords Dance','X-Scissor']},

    ##T
    'Tyranitar' : {'stats':(100,134,110,95,100,61),'type1':'Rock','type2':'Dark','moves':['Brick Break','Crunch','Earthquake','Fire Fang','Ice Fang','Iron Defense','Protect','Rock Blast','Rock Slide','Screech','Shadow Claw','Stone Edge','Thunder Fang']},
    
    }
natures = [
    ['Adamant',(1, 1.1, 1, 0.9, 1, 1)]
           ]

stages = {
    '-6' : 2/8,
    '-5' : 2/7,
    '-4' : 2/6,
    '-3' : 2/5,
    '-2' : 2/4,
    '-1' : 2/3,
    '0' : 2/2,
    '1' : 3/2,
    '2' : 4/2,
    '3' : 5/2,
    '4' : 6/2,
    '5' : 7/2,
    '6' : 8/2
    }

accStages = {
    '-6' : 3/9,
    '-5' : 3/8,
    '-4' : 3/7,
    '-3' : 3/6,
    '-2' : 3/5,
    '-1' : 3/4,
    '0' : 3/3,
    '1' : 4/3,
    '2' : 5/3,
    '3' : 6/3,
    '4' : 7/3,
    '5' : 8/3,
    '6' : 9/3
    }

evasStages = {
    '6' : 3/9,
    '5' : 3/8,
    '4' : 3/7,
    '3' : 3/6,
    '2' : 3/5,
    '1' : 3/4,
    '0' : 3/3,
    '-1' : 4/3,
    '-2' : 5/3,
    '-3' : 6/3,
    '-4' : 7/3,
    '-5' : 8/3,
    '-6' : 9/3
    }

weakness = {
    'Bug' : ['Fire','Flying','Rock'],
    'Dark' : ['Fighting','Bug','Fairy'],
    'Dragon' : ['Dragon','Fairy','Ice'],
    'Electric' : ['Ground'],
    'Fairy' : ['Steel','Poison'],
    'Fighting' : ['Psychic','Flying','Fairy'],
    'Fire' : ['Water','Ground','Rock'],
    'Flying' : ['Electric','Ice','Rock'],
    'Ghost' : ['Ghost','Dark'],
    'Grass' : ['Fire','Ice','Poison','Flying','Bug'],
    'Ground' : ['Water','Grass','Ice'],
    'Ice' : ['Fire','Fighting','Rock','Steel'],
    'Normal' : ['Fighting'],
    'Poison' : ['Ground','Psychic'],
    'Psychic' : ['Bug','Dark','Ghost'],
    'Rock' : ['Water','Grass','Fighting','Ground','Steel'],
    'Steel' : ['Fire','Ground','Fighting'],
    'Water' : ['Electric','Grass'],
    '' : []
    }

resistance = {
    'Bug' : ['Grass','Fighting','Ground'],
    'Dark' : ['Ghost','Dark'],
    'Dragon' : ['Fire','Water','Grass','Electric'],
    'Electric' : ['Electric','Flying'],
    'Fairy' : ['Fighting','Bug','Dark'],
    'Fighting' : ['Bug','Rock','Dark'],
    'Fire' : ['Fire','Grass','Ice','Bug','Steel','Fairy'],
    'Flying' : ['Grass','Fighting','Bug'],
    'Ghost' : ['Poison','Bug'],
    'Grass' : ['Water','Electric','Grass','Ground'],
    'Ground' : ['Poison','Rock'],
    'Ice' : ['Ice'],
    'Normal' : [],
    'Poison' : ['Grass','Fighting','Poison','Bug','Fairy'],
    'Psychic' : ['Fighting','Psychic'],
    'Rock' : ['Normal','Fire','Poison','Flying'],
    'Steel' : ['Normal','Grass','Ice','Flying','Psychic','Bug','Rock','Dragon','Steel','Fairy'],
    'Water' : ['Fire','Water','Ice','Steel'],
    '' : [],
    }

immune = {
    'Bug' : [],
    'Dark' : ['Psychic'],
    'Dragon' : [],
    'Electric' : [],
    'Fairy' : ['Dragon'],
    'Fighting' : [],
    'Fire' : [],
    'Flying' : ['Ground'],
    'Ghost' : ['Normal','Fighting'],
    'Grass' : [],
    'Ground' : ['Electric'],
    'Ice' : [],
    'Normal' : ['Ghost'],
    'Poison' : [],
    'Psychic' : [],
    'Rock' : [],
    'Steel' : ['Poison'],
    'Water' : [],
    '' : []
    }
    

templateForTypes = {
    'Bug' : [],
    'Dark' : [],
    'Dragon' : [],
    'Electric' : [],
    'Fairy' : [],
    'Fighting' : [],
    'Fire' : [],
    'Flying' : [],
    'Ghost' : [],
    'Grass' : [],
    'Ground' : [],
    'Ice' : [],
    'Normal' : [],
    'Poison' : [],
    'Psychic' : [],
    'Rock' : [],
    'Steel' : [],
    'Water' : [],
    }
