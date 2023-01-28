##Meu primeiro app

import streamlit as st
import pandas as pd
import flet 

variavel = input('Digite o nome da variavel:')

df = pd.DataFrame({
    'primeiraColuna':[1,2,3,4],
    'segundaColuna':[10,20,30,40]
})

df
