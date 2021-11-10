import unittest
# from .. import utils



def test_split_string_discord():
    """
    test the string split functionality for discord notification
    """
    test_string = """
    If you’re an arcade racing game purist, Burnout Paradise has a lot to answer for. By taking the classic series open-world, Criterion essentially obsoleted the concept of traditional racers — here are your cars, here are your tracks, learn to drive the former to perfect the latter — at least in the eyes of major publishers. Ever since, virtually all big-budget arcade racing games have been made in the shadow of Paradise, with most tracks consisting of lines drawn across vast, explorable maps.
    As someone who is personally not very happy about this turn of events, I have to admit that Microsoft’s Forza Horizon series has been a pretty spectacular product of it all. With each entry in the series, developer Playground Games has delivered relentlessly entertaining open-world racing in vividly rendered settings. Forza Horizon 5, the latest release, relocates to Mexico and turns out to be the best Forza Horizon yet — as well as one of the best games of the year.
    The previous game in the series, Forza Horizon 4, was personally appealing to me because of its UK setting, which I found to be a convincing rendering of where I grew up. But I found the game hard to get into because of the way it handled its open-world design, throwing an overwhelming array of cars and quests at you. Every time I opened the game after a week or two away, I’d have no idea what to do — the overwrought UI gave me option paralysis. It felt more like Assassin’s Creed on wheels than an arcade racer.

    Forza Horizon 5 doesn’t change the basic structure, and there’s still a huge amount of stuff dotting the Mexican map. But it does do a better job of easing you into its mountain of content. You’re able to choose which specific types of events to unlock as you progress, so, for example, I preferred to focus on closed-track road races early on before delving into cross-country rallies. I feel like if I stopped playing the game and came back to it weeks later, I’d have a much better sense of what I’d been doing and where would be best for me to spend the next couple of hours. In turn, that makes me feel better about simply driving around the landscape in search of whatever esoteric quest I might come across. Unlike with 4, I’ve never felt like I’m wasting my time in Forza Horizon 5, as I always have more of a sense of what I could be working toward.

    FORZA HORIZON 5 DOES DO A BETTER JOB OF EASING YOU INTO ITS MOUNTAIN OF CONTENT
    Forza Horizon’s premise — a “festival” that descends on a loosely recreated real-world locale and takes it over with various racing events of dubious legality — remains as absurd as ever, with entirely superfluous “story” sequences peppered throughout. I have personally never been to Mexico, but I have a feeling most of the locals wouldn’t take too kindly to visitors causing wanton destruction while bombing around the streets in a Dodge Viper listening to Dua Lipa.
    Despite the name and the hundreds of accurately modeled real-world cars, Forza Horizon has little in common with Turn 10 Studios’ Forza Motorsport series, which is more of a serious racing simulator. While Horizon isn’t exactly a Ridge Racer-style arcade game, it’s certainly on the more accessible side of things. The physics feel somewhat grounded in reality, and you’ll notice big differences in how various cars handle, but the driving model is very forgiving, and it’s easy for anyone to pick up and play.
    """

    print(utils.split_string_discord(test_string))

    # assert sum([1, 2, 3]) == 6, "Should be 6"