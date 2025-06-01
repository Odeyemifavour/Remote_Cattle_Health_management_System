<<template>
    <div class="card">
        <h2 class="card-title">Settings & Help</h2>
        <p class="message-center">Manage application settings and access help resources here.</p>
        <p class="message-center developer-info">
            This is a Remote Livestock Management System.<br>
            Developed by: Odeyemi Favour Abosede<br>
            Contact: <a href="mailto:odeyemifavour593@gmail.com">odeyemifavour593@gmail.com</a>
        </p>
    </div>
</template>

<script setup>
// No specific logic needed
</script>

<style scoped>
.developer-info {
    margin-top: 30px;
    border-top: 1px solid var(--border-color);
    padding-top: 20px;
    font-size: 0.9em;
    color: var(--text-secondary);
}
.developer-info a {
    color: var(--primary-color);
    text-decoration: none;
}
.developer-info a:hover {
    text-decoration: underline;
}
</style>
