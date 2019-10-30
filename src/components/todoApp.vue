<template>
  <div class="todoApp">
    <div class="form-group">
      <h1>
        <span class="vue">Vue</span> To-Do
        <small>List</small>
      </h1>
      <form role="form">
        <input
          type="text"
          class="form-control"
          placeholder="해야 할 일"
          v-model="title"
          v-on:keyup.enter="addTodo(title)"
        />
      </form>
      <button type="button" v-on:click="addTodo(title)" class="btn btn btn-primary">Add</button>
    </div>
    <div class="todo-list">
      <!-- todoList 컴포넌트: v-bind(디렉티브) Element 객체의 속성 동적 데이터 바인딩 -->
      <todoList v-bind:todos="todos" v-on:del-todo="delTodo"></todoList>

      <br />
      <br />
      <router-link to="/todoRestful" tag="button" class="btn btn-success">Restful</router-link>
    </div>
  </div>
</template>



// <script>
// // todoList 컴포넌트 import
// import todoList from "@/components/todoList";
// export default {
//   name: "todoApp",
//   // data
//   data() {
//     return {
//       title: "",
//       todos: [
//         {
//           title: "운동하기"
//         },
//         {
//           title: "JAVA"
//         },
//         {
//           title: "javascript"
//         },
//         {
//           title: "영어"
//         }
//       ]
//     };
//   },
//   methods: {
//     addTodo(title) {
//       if (title) {
//         this.todos.push({ title: title });
//         this.title = "";
//       }
//     },
//     delTodo(todo) {
//       this.todos.splice(todo, 1);
//     }
//   },
//   components: {
//     todoList: todoList
//   }
// };
//
//
</script>

<script>
import todoList from "@/components/todoList";
export default {
  name: "todoApp-restful",
  // data
  data() {
    return {
      title: "",
      todos: []
    };
  },
  methods: {
    getTodos() {
      this.$http.get("http://localhost:3000/todoData").then(res => {
        this.todos = res.data;
      });
    },
    addTodo(title) {
      console.log("title", title);

      if (title) {
        this.$http
          .post("http://localhost:3000/todoData", {
            title: title
          })
          .then(res => {
            this.todos.push(res.data);
            this.title = "";
          });
      }
    },
    delTodo(todo) {
      this.$http.delete("http://localhost:3000/todoData/" + todo).then(res => {
        this.getTodos();
      });
    }
  },
  mounted() {
    this.getTodos();
  },
  components: {
    todoList: todoList
  }
};
</script>

<style scoped>
.todoApp {
  margin: auto;
  width: 500px;
}
form {
  display: inline-block;
}
.form-group {
  text-align: center;
  margin-top: 10em;
  padding-bottom: 25px;
}
.todo-list {
  width: 250px;
  text-align: left;
  margin-left: 130px;
}
a.close {
  float: right;
}
.vue {
  color: #009900;
}
</style>