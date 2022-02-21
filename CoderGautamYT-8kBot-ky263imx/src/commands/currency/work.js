const Discord = require('discord.js')
const jobjson = require("../../json/jobs.json")
const fs = require('fs');
const jobfiles = new Discord.Collection();

const jobarray = fs.readdirSync("./src/jobs").filter(file => file.endsWith('.js'));
for (const file of jobarray) {
    const jobdata = require(`../../jobs/${file}`);
    jobfiles.set(jobdata.name, jobdata);
}
const api = require("../../core/api")
const simpleCommand = require("../../core/simpleCommand")

module.exports = new simpleCommand(
    async(message, args, client, addCD) => {
        var user = await api.getUser(message.author.id)
        if (!user.hasOwnProperty("job")) {
            user.job = { exists: false }
        }
        if (user.job.exists) {
            jobfiles.get(user.job.name).work(message, (moneyEarned) => {
                var dafunc = (typeof moneyEarned == "number" ? api.changeBal : api.modUser)
                dafunc(message.author.id, moneyEarned)
                    .then(() => {
                        api.addCool(message.author.id, "work", (jobjson.hasOwnProperty(user.job.name.toLowerCase()) ? jobjson[user.job.name][2] : 900000))
                    })


            }, user)
        } else {
            const embed = new Discord.MessageEmbed()
                .setColor('#0099ff')
                .setTitle("You dont have an job! View a list of jobs by typing `8k!jobs`")
            message.channel.send(embed)
        }

    }, {
        name: "work",
        aliases: ["work"],
        cooldown: 0,
        cooldownMessage: "Too much work is a bad thing, you can work again in **{timeleft}**",
        perms: ["SEND_MESSAGES"],
        usage: "{prefix}{cmd}",
        description: "Lets you work at your job, you can get a job by typing `8k!joblist`"
    }
)
