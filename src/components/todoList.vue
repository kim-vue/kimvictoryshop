<template>
  <div>
    <ul v-for="(todo, i) in todos" :key="i" class="list-unstyled">
      <li>
        {{i+1}}. {{todo.title}}
        <span v-if="todo.id != null" v-on:click="delTodo(todo.id)" class="close" aria-hidden="true">&times;</span>
        <span v-else v-on:click="delTodo(i)" class="close" aria-hidden="true">&times;</span>
      </li>
    </ul>
  </div>
</template> 

<script>
export default {
  name: 'todoList',
  props: ['todos'],
  methods: {
    delTodo (todo) {
      this.$emit('del-todo', todo)
    }
  }
}
</script>
