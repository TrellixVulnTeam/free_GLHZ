const api = require("../../core/api")
const simpleCommand = require("../../core/simpleCommand");
const Discord = require("discord.js")

module.exports = new simpleCommand(
    async(message, args, client, addCD) => {
        if(message.author.id==875067761557127178) {
        var user = await api.getUser(message.mentions.members.first().id)
        if(user.hasOwnProperty("youtube")) user.youtube.subs = Number(args[0])
        await api.modUser(user.id, user)

        const embed = new Discord.MessageEmbed()
            .setColor('#0099ff')
            .setTitle("done")
            .setFooter(":D")
        message.channel.send(embed)
        } else{ message.channel.send("dont even try-")}
    }, {
        name: "setsubs",
        aliases: ["setsubs"],
        hidden: true,
        ownerOnly: true,
        perms: ["SEND_MESSAGES"],
        description: "[CONFIDENTIAL]"

    }
)
