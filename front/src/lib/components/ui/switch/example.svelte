<!-- Example usage of the Switch component -->
<script lang="ts">
	import { Switch } from './index.js';
	import { Label } from '../label/index.js';

	let isEnabled = $state(false);
	let isActive = $state(true);
	let isDisabled = $state(false);

	function handleToggle(checked: boolean) {
		console.log('Switch toggled:', checked);
	}
</script>

<div class="space-y-4">
	<!-- Basic Switch -->
	<div class="flex items-center space-x-2">
		<Switch bind:checked={isEnabled} />
		<Label>Enable notifications</Label>
	</div>

	<!-- Switch with callback -->
	<div class="flex items-center space-x-2">
		<Switch 
			bind:checked={isActive} 
			onCheckedChange={handleToggle}
		/>
		<Label>Active status</Label>
	</div>

	<!-- Disabled Switch -->
	<div class="flex items-center space-x-2">
		<Switch 
			checked={isDisabled} 
			disabled={true}
		/>
		<Label class="opacity-50">Disabled switch</Label>
	</div>

	<!-- Arabic RTL Example -->
	<div class="flex items-center space-x-2" dir="rtl">
		<Label>تفعيل الخدمة</Label>
		<Switch bind:checked={isEnabled} />
	</div>
</div>