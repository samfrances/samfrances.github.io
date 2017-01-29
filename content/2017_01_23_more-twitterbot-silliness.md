Title: More twitterbot silliness
Date: 2017-1-23 23:41
UniqueId: 2017-1-23-more-twitterbot-silliness-020793ff-5c2f-4b36-87be-71e84efb256d
Modified:
Category: Blog
Tags: javascript, node, aws, ansible
Slug: more-twitterbot-silliness
Authors:
Summary: Not content to rest on my laurels after the roaring success that was [@fight_guybrush](https://twitter.com/fight_guybrush), I have written another twitter bot.



Not content to rest on my laurels after the roaring success that was [@fight_guybrush](https://twitter.com/fight_guybrush), I have written another twitter bot, [@grauniad_news](https://twitter.com/grauniad_news), an exact replica of the twitter feed for The Guardian newspaper, but with added spelling mistakes.

(For any non-British readers, The Guardian is a UK newspaper with a reputation for spelling mistakes, among other things, giving rise to the nickname "The Grauniad".)

This bot is a slightly more sophisticated project than the last one, which was just a python script triggered hourly by cron. The new bot is written in node.js, uses Twitter's streaming API to monitor and respond to tweets in real time, and is hosted on an Amazon Web Services t2.nano instance, launched using Ansible. I use the [Twit](https://github.com/ttezel/twit) library to communicate with Twitter's API, and [forever](https://github.com/foreverjs/forever) to ensure that the bot keeps running continuously.

The method of generating badly spelled tweets is quite simple, but even so, it taught me some important lessons. The most important lesson: watch out for infinite loops in node. Early on, I found that the twitterbot would freeze after a seemingly random interval during which it worked normally. No errors were logged, and `forever list` showed the program as still running.

The problem turned out to be in my simple function for introducing misspellings.

    :::javascript
    function misspellRandomWords(sentence) {
        let words = sentence.split(" ");
        const limit = words.length;

        // Choose a first word, filtering out urls
        var iFirstWord = Math.floor(Math.random() * limit);
        while (isLink(words[iFirstWord]) || words[iFirstWord][0] === "@" ) {
            iFirstWord = Math.floor(Math.random() * limit);
        }

        // Choose second misspelled word, and make sure it isn't the first or an URL
        var iSecondWord = Math.floor(Math.random() * limit);
        while (isLink(words[iSecondWord]) ||
                iSecondWord === iFirstWord ||
                words[iSecondWord][0] === "@") {
            iSecondWord = Math.floor(Math.random() * limit);
        }

        words[iFirstWord] = swapRandomLetters(words[iFirstWord]);
        words[iSecondWord] = swapRandomLetters(words[iSecondWord]);

        return words.join(" ");
    }

This worked most of the time, but would get into an infinite loop in certain circumstances - for example, if every word in the tweet starts with "@".

I don't know if this is how a node.js expert would do it, but after resolving this bug, I started guarding my loops to catch any unforeseen conditions that would cause them to loop infinitely, and make sure that these were logged as errors.

    :::javascript
    function misspellRandomWords(sentence) {
    // ...
    // ...
        let nLoops = 0; // Infinite loop error detection
        while (!isSwappable(words[iFirstWord])) {
            iFirstWord = Math.floor(Math.random() * limit);

            // Infinite loop detection
            if (++nLoops > 1000) {
                console.error("Infinite loop detected on sentence: " + sentence);
            }

        }
    // ...
    // ...
    }

If you're interested, you can take a look at the code [on Github](https://github.com/samfrances/grauniad-node), or have a look at the bot [on Twitter](https://twitter.com/grauniad_news). Be warned, the bot is not sophisticated enough to know when a randomly misspelled headline might cause offence.
