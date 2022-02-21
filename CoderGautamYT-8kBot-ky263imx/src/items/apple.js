const Discord = require('discord.js')
const api = require('../core/api')

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
module.exports = {

    name: 'apple',
    use(message, userItem, user) {
        api.checkCool(message.author.id, "apple")
            .then((cooldown) => {
                if (cooldown.cooldown) {
                    const embed = new Discord.MessageEmbed()
                        .setColor('#0099ff')
                        .setTitle("Cooldown")
                        .setDescription("You just ate an apple!\nYou can eat another one in `" + api.convertMS(cooldown.msleft) + "`")
                    message.channel.send(embed)
                } else {
                    if (getRandomInt(1, 50) == 7) {
                        var moneyEarn = 50000
                        var type = "LEGENDARY GOLDEN APPLE. YUM!"
                    } else {
                        var dfgd = Math.floor(Math.random() * 8 + 1)
                        if (dfgd == 1) {
                            var moneyEarn = 0
                            var type = "Rotten apple *bleh*"
                        } else if (dfgd == 2) {
                            var moneyEarn = 500
                            var type = "Old apple.. "
                        } else if (dfgd == 3 || dfgd == 4 || dfgd == 5 || dfgd == 6) {
                            var moneyEarn = 1100
                            var type = "Sour apple. 🍏*nice* "
                        } else if (dfgd == 7 || dfgd == 8) {
                            var moneyEarn = 2000
                            var type = "Red apple. 🍎*yum* "
                        }
                    }
                    user.inv.apple.amount = userItem.amount - 1
                    user.bal = user.bal + moneyEarn
                    if (user.inv.apple.amount == 0) {
                        delete user.inv.apple
                    }
                    api.modUser(message.author.id, user)
                        .then(() => {
                            const embed = new Discord.MessageEmbed()
                                .setTitle("Ate apple")
                                .setDescription("That was a " + type + "\nYou got `" + moneyEarn + "` coins!")

                            message.channel.send(embed)
                            api.addCool(message.author.id, "apple", 5000)
                                .catch(() => {

                                })
                        })

                    .catch(() => {
                        message.channel.send("Something went wrongg")
                    })
                }
            })
    }
}