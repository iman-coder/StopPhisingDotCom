<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
      <a class="navbar-brand" href="#">StopPhishingdotcom</a>

      <div class="navbar-nav">
        <router-link to="/" class="nav-link">Dashboard</router-link>
        <router-link to="/urls" class="nav-link">Manage URLs</router-link>
      </div>
    </nav>

    <div class="container mt-4">
      <router-view />
    </div>
  </div>
</template>

<!--The api endpoints:
POST /urls/import
GET /urls/export
GET /urls
POST /urls
DELETE /urls/{id}
PUT /urls/{id} -->
