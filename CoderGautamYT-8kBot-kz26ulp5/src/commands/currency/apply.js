const api = require("../../core/api")
const simpleCommand = require("../../core/simpleCommand");
const Discord = require("discord.js");
const jobs = require('../../json/jobs.json')
const fs = require("fs")
const jobfiles = new Discord.Collection();
const jobarray = fs.readdirSync('./src/jobs/').filter(file => file.endsWith('.js'));
for (const file of jobarray) {
    const jobdata = require(`../../jobs/${file}`);
    jobfiles.set(jobdata.name, jobdata);
    console.log("Initialized " + `./jobs/${file}`)
}
module.exports = new simpleCommand(
    async(message, args, client, addCD) => {
        var user = await api.getUser(message.author.id)

        var job = args.join(' ').toLowerCase()
        if (jobs.hasOwnProperty(job)) {

            //add inventory if does not exist
            if (!user.hasOwnProperty("job")) {
                user.job = { exists: false }
            }


            //check if already have job
            if (user.job.exists) {
                const embed = new Discord.MessageEmbed()
                    .setColor('BLUE')
                    .setTitle("Already Have a job!")
                    .setDescription("You already work as a `" + user.job.name + "`!")
                message.channel.send(embed)
            } else {
                api.checkCool(message.author.id, "applyfail")
                    .then((cooldown) => {

                        if (cooldown.cooldown) {

                            const embed = new Discord.MessageEmbed()
                                .setColor('#0099ff')
                                .setTitle("Cooldown")
                                .setDescription("You failed your previous job interview\nYou can apply for a job in `" + api.convertMS(cooldown.msleft) + "`")
                            message.channel.send(embed)
                        } else {
                            jobfiles.get(job).interview(message, (pass) => {

                                message.channel.send("COLLECTING RESULTS...")
                                    .then((msg11) => {
                                        setTimeout(() => {
                                            msg11.edit("DID YOU MAKE IT?")
                                                .then((msg22) => {
                                                    setTimeout(async() => {
                                                        if (pass) {
                                                            user.job = {
                                                                exists: true,
                                                                name: job
                                                            }
                                                            await api.modUser(message.author.id, user)
                                                            const embed = new Discord.MessageEmbed()
                                                                .setColor('RED')
                                                                .setTitle(user.name + " Passed Job Interview!")
                                                                .setDescription("🥳🥳YOU DID IT!!!!\nYou are now a `" + job + "`!!!!🥳🥳")
                                                                .setFooter("You can start working by typing `8k!work`")
                                                            msg22.delete()
                                                            message.channel.send(embed)




                                                        } else {
                                                            await addCD()
                                                            const embed = new Discord.MessageEmbed()
                                                                .setColor('RED')
                                                                .setTitle(user.name + " Failed Job Interview")
                                                                .setDescription("too bad so sad YOU FAILED 😠\nTry again later...")
                                                            msg22.delete()
                                                            message.channel.send(embed)

                                                        }
                                                    }, 1000)
                                                })
                                        }, 1000)
                                    })
                            }, user)
                        }
                    })

            }




        } else {
            if (job == "") {
                const embed = new Discord.MessageEmbed()
                    .setColor('RED')
                    .setTitle("No job entered")
                    .setDescription("Please use the command like `8k!apply <jobname>`\nType `8k!jobs` for a list of jobs")
                message.channel.send(embed)
            } else {
                const embed = new Discord.MessageEmbed()
                    .setColor('RED')
                    .setTitle("Not found")
                    .setDescription("The job `" + job + "` was not found\nType `8k!jobs` for a list of jobs")
                message.channel.send(embed)
            }

        }



    }, {
        name: "apply",
        aliases: ["apply", "jobapply"],
        cooldown: 43200000,
        cooldownMessage: "You failed your previous job interview\nYou can apply for a job in **{timeleft}**",
        perms: ["SEND_MESSAGES"],
        description: "Apply for a job <jobname>! You can view a list of the available jobs by typing 8k!jobs",
        usage: "{prefix}{cmd} <jobname>"
    }
)