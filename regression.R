data_c = read.csv("regression.csv")
png(filename="2_result_a.png")
plot(data_c)
abline(lm(y ~ x, data=data_c), col="red")
dev.off()
lm_result <- lm(y ~ x, data=data_c)
print(lm_result)
coefficients(lm_result)
summary(lm_result)

