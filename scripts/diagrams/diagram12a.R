source("diagram12.R")

diagram <- ggplot(data = dat,
                  aes(x = genauthor,
                      stat = "identity",
                      fill = label)) +
  geom_bar(position = position_dodge2(preserve = "single")) +
  labs(x = "", y = "#Tests") +
  theme(legend.position = "bottom") +
  scale_fill_manual(values = diagramColorScheme,
                    name = "Result:")
diagram