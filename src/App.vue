<template>
  <div id="app">
    <img id="logo" src="./src/assets/logo.png" alt="oscar" />
    <h1>Oscar Awards</h1>
    <div class="container">
      <div class="input-group">
        <label for="tipoPesquisa">Tipo de Pesquisa:</label>
        <select v-model="tipoPesquisa" @change="buscarInformacoes">
          <option value="vencedores">Vencedores</option>
          <option value="nao_vencedores">Não Vencedores</option>
        </select>
      </div>
      <div class="input-group">
        <label for="ano">Ano:</label>
        <select v-model="anoSelecionado" @change="buscarInformacoes">
          <option v-for="ano in anosDisponiveis" :key="ano" :value="ano">{{ ano }}</option>
        </select>
      </div>
      <div class="resultados" v-if="informacoes.length > 0">
        <!--<h2>Resultados</h2>-->
        <div v-for="(categoria, indice) in informacoes" :key="indice">
          <!--<h3>{{ indice }}</h3>-->
          <ul>
            <li v-for="(vencedor, nomeCategoria) in categoria" :key="nomeCategoria">
              <h3><i class="fa-solid fa-award" style="color: #e8ac38"></i> {{ nomeCategoria }}</h3>
              <div id="respostas"><span  v-html="vencedor"></span></div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  data() {
    return {
      tipoPesquisa: "vencedores",
      anoSelecionado: null,
      anosDisponiveis: [],
      informacoes: [],
    };
  },
  mounted() {
    // Obter anos disponíveis do Flask
    this.obterAnosDisponiveis();
  },
  methods: {
    async obterAnosDisponiveis() {
      try {
        const response = await fetch("https://jogos.evertontenorio.tech/anos");
        const data = await response.json();
        this.anosDisponiveis = data.slice().reverse();
        // Definir um ano padrão
        this.anoSelecionado = this.anosDisponiveis[0];
        // Buscar informações ao carregar a página
        this.buscarInformacoes();
      } catch (error) {
        console.error("Erro ao obter anos disponíveis:", error);
      }
    },
    async buscarInformacoes() {
      try {
        const response = await fetch(
          `https://jogos.evertontenorio.tech/${this.tipoPesquisa}/${this.anoSelecionado}`
        );
        const data = await response.json();

        if (data.length > 0 && this.tipoPesquisa === 'vencedores') {
          for (const categoria in data[0]) {
            if (data[0][categoria].length > 0) {
              data[0][categoria] = data[0][categoria].replace(
                /([^,]+),\s+Nome original: (.+)/,
                `$1 <br> <span style="color: #9d9d9d; font-size: 12px">Nome original: $2</span>`
              );
            }
          }
        }

        this.informacoes = data;
      } catch (error) {
        console.error("Erro ao buscar informações:", error);
      }
    },
  },
};
</script>

<style>
@import "./styles/styles.css";
</style>
