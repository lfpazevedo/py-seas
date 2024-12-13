#X13-------------------------------------------------------------
local <- paste0("/home/lfpazevedo/Documents/Projects/x13as/")
Sys.setenv(X13_PATH = local)

library(seasonal)
library(readxl)
library(curl)
library(lubridate)

#===============================
#Feriados
#===============================

url <- 'https://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls'

tf <- tempfile(fileext = ".xls")
curl_download(url, tf)
anbima <- read_excel(tf, 1L, range = "A1:C937")
anbima$Data <- as.Date(anbima$Data)
anbima$Ano <- floor_date(anbima$Data, 'year')

range_feriados <- length(as.data.frame(table(anbima$Ano))$Var1)
dias_Ano <- as.Date(as.data.frame(table(anbima$Ano))$Var1)

feriados <- data.frame(matrix(ncol = 4, nrow = range_feriados))
colnames(feriados) <- c("Ano","Carnaval","Pascoa","Corpus")

dias_Carnaval <- anbima$Data[anbima$Feriado=="Carnaval"]

for(i in 2:length(dias_Carnaval)) {
  if  (difftime(dias_Carnaval[i],dias_Carnaval[i-1],
                units = 'days') == 1) {
    dias_Carnaval[i-1] = NA
  }
}
dias_Carnaval <- na.omit(dias_Carnaval)

dias_Pascoa <- anbima$Data[anbima$Feriado=="Paixão de Cristo"]
dias_Corpus <- anbima$Data[anbima$Feriado=="Corpus Christi"]

feriados$Ano <- dias_Ano
feriados$Carnaval <- dias_Carnaval
feriados$Pascoa <- dias_Pascoa
feriados$Corpus <- dias_Corpus

#IBGE usou 02/mar/22 como referência para Carnaval, e não 01/mar/22
feriados$Carnaval[feriados$Carnaval == '2022-03-01'] <- '2022-03-02'

#IBGE usou 05/mar/03 como referência para Carnaval, e não 04/mar/03
feriados$Carnaval[feriados$Carnaval == '2003-03-04'] <- '2003-03-05'

#IBGE usou 05/mar/14 como referência para Carnaval, e não 04/mar/14
feriados$Carnaval[feriados$Carnaval == '2014-03-04'] <- '2014-03-05'

#IBGE usou 05/mar/25 como referência para Carnaval, e não 04/mar/25
feriados$Carnaval[feriados$Carnaval == '2025-03-04'] <- '2025-03-05'


range_func <- function(x,y){feriados[feriados[,1] >= x & feriados[,1] <= y,]}
start_date <- as.Date("2001/1/1")              #um ano antes do início da série
end_date <- as.Date("2025/1/1")                #um ano após o ano corrente
range_feriados <- range_func(start_date,end_date)


#===============================
#Genhol
#===============================
#Pascoa
pascoa <- genhol(range_feriados$Pascoa, start = -8, frequency = 12, center = "calendar")

#Carnaval-------------------------------------------------------------
carnaval <- genhol(range_feriados$Carnaval, start = -4, end = -1, frequency = 12, center = "calendar")

#Corpus_Christi-------------------------------------------------------------
corpus <- genhol(range_feriados$Corpus, start = 1, end = 3, frequency = 12, center = "calendar")
#------------------------------------------------------------------------------------

#========================================
#Save

regs_R <- na.omit(cbind("aux",carnaval, pascoa, corpus))

print(regs_R) 
# write.csv2(regs_R, file = "C:\\ECONOMIA_20200314\\SEAS\\Regressores\\Regs_R.csv")
#========================================